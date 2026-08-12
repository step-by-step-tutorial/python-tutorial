import logging
from datetime import datetime

from itables import show

from app_config import env_config as ec
from audit.audit_service import AuditService
from dataset.definition import Dataset
from model.audit_metrics import AuditMetrics
from service.database import database_sale_service
from service.datalake import inmemory_datalake_service
from service.datawarehouse import datawarehouse_sale_service
from util.csv_utils import csv_to_dataframe
from util.datalake_utils import DatalakeLayer, generate_full_path, generate_relative_path
from util.file_utils import absolute_path
from util.log_utils import log_line
from util.pandas_dataframe_utils import require_columns, show_map_of_dataframe
from util.pipeline_utils import create_pipeline_id
from util.time_utils import generate_ingestion_time

logger = logging.getLogger(__name__)


class InmemoryAuditablePipeline:

    def __init__(self, ds: Dataset) -> None:
        self.dataset = ds
        self.pipeline_name = "inmemory_auditable_pipeline"
        self.pipeline_id = create_pipeline_id()
        self.ingestion_time: datetime = generate_ingestion_time()
        self.task_attempt = 1
        self.raw_row_count = 0
        self.cleaned_row_count = 0
        self.enriched_row_count = 0
        self.audit_service = AuditService()

    def run(self) -> None:
        pipeline_started_at = self.audit_service.start_pipeline(
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            metadata={
                "dataset": self.dataset.name,
                "ingestion_time": self.ingestion_time.isoformat()
            }
        )

        logger.info(
            "Starting ETL pipeline with dataset %s, pipeline id %s at ingestion time %s",
            self.dataset.name,
            self.pipeline_id,
            self.ingestion_time.isoformat()
        )
        log_line()

        logger.info("step 1")
        raw_relative_path = self.store_raw_data()
        log_line()

        logger.info("step 2")
        cleaned_relative_path = self.cleaning(raw_relative_path)
        log_line()

        logger.info("step 3")
        enriched_relative_path = self.enriching(cleaned_relative_path)
        log_line()

        logger.info("step 4")
        self.populate_database(enriched_relative_path)
        log_line()

        logger.info("step 5")
        self.populate_datawarehouse(enriched_relative_path)
        log_line()

        logger.info("step 6")
        self.show_dataframe(enriched_relative_path)

        logger.info("step 7")
        self.analyzing_via_memory(enriched_relative_path)
        log_line()

        logger.info("step 8")
        self.analyzing_via_datawarehouse()
        log_line()

        self.audit_service.complete_pipeline(
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            started_at=pipeline_started_at,
            input_row_count=self.raw_row_count,
            output_row_count=self.enriched_row_count,
            rejected_row_count=self.raw_row_count - self.cleaned_row_count,
            metadata={
                "dataset": self.dataset.name,
                "ingestion_time": self.ingestion_time.isoformat(),
                "raw_path": raw_relative_path,
                "cleaned_path": cleaned_relative_path,
                "enriched_path": enriched_relative_path,
                "cleaned_row_count": self.cleaned_row_count
            }
        )

        logger.info(
            "Finished ETL pipeline with dataset %s, pipeline id %s at ingestion time %s",
            self.dataset.name,
            self.pipeline_id,
            self.ingestion_time.isoformat()
        )

    def store_raw_data(self) -> str:
        metrics = AuditMetrics()

        context, started_at = self.audit_service.start_task(
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            task_name="store_raw_data",
            task_attempt=self.task_attempt,
            metrics=metrics
        )

        data_file_path = absolute_path(ec.RESOURCES_DIR) / self.dataset.file_name
        dataframe = csv_to_dataframe(data_file_path)
        require_columns(dataframe, self.dataset.required_columns)

        self.raw_row_count = len(dataframe)

        relative_path = generate_relative_path(DatalakeLayer.RAW, self.ingestion_time)
        full_path = generate_full_path(self.dataset.datalake.bucket_name, relative_path)

        metrics.input_row_count = self.raw_row_count
        metrics.output_row_count = self.raw_row_count
        metrics.source_system = "csv"
        metrics.source_uri = str(data_file_path)
        metrics.destination_system = "datalake"
        metrics.destination_uri = full_path

        inmemory_datalake_service.upload(
            df=dataframe,
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=relative_path
        )

        self.audit_service.write_dataset(
            source_system="csv",
            source_uri=str(data_file_path),
            destination_system="datalake",
            destination_uri=full_path,
            row_count=self.raw_row_count,
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            metadata={"datalake_layer": DatalakeLayer.RAW.value}
        )

        self.audit_service.complete_task(context, started_at)

        return relative_path

    def cleaning(self, raw_relative_path: str) -> str:
        metrics = AuditMetrics()

        context, started_at = self.audit_service.start_task(
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            task_name="cleaning",
            task_attempt=self.task_attempt,
            metrics=metrics
        )

        dataframe = inmemory_datalake_service.download(
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=raw_relative_path
        )

        raw_full_path = generate_full_path(self.dataset.datalake.bucket_name, raw_relative_path)
        input_row_count = len(dataframe)

        self.audit_service.read_dataset(
            source_system="datalake",
            source_uri=raw_full_path,
            row_count=input_row_count,
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            metadata={"datalake_layer": DatalakeLayer.RAW.value}
        )

        cleaned_dataframe = self.dataset.processors["inmemory"].clean(dataframe)
        self.cleaned_row_count = len(cleaned_dataframe)

        relative_path = generate_relative_path(DatalakeLayer.CLEANED, self.ingestion_time)
        cleaned_full_path = generate_full_path(self.dataset.datalake.bucket_name, relative_path)

        metrics.input_row_count = input_row_count
        metrics.output_row_count = self.cleaned_row_count
        metrics.rejected_row_count = input_row_count - self.cleaned_row_count
        metrics.source_system = "datalake"
        metrics.source_uri = raw_full_path
        metrics.destination_system = "datalake"
        metrics.destination_uri = cleaned_full_path

        inmemory_datalake_service.upload(
            df=cleaned_dataframe,
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=relative_path
        )

        self.audit_service.write_dataset(
            source_system="datalake",
            source_uri=raw_full_path,
            destination_system="datalake",
            destination_uri=cleaned_full_path,
            row_count=self.cleaned_row_count,
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            metadata={"datalake_layer": DatalakeLayer.CLEANED.value}
        )

        self.audit_service.complete_task(context, started_at)

        return relative_path

    def enriching(self, cleaned_relative_path: str) -> str:
        metrics = AuditMetrics()

        context, started_at = self.audit_service.start_task(
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            task_name="enriching",
            task_attempt=self.task_attempt,
            metrics=metrics
        )

        dataframe = inmemory_datalake_service.download(
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=cleaned_relative_path
        )

        cleaned_full_path = generate_full_path(self.dataset.datalake.bucket_name, cleaned_relative_path)
        input_row_count = len(dataframe)

        self.audit_service.read_dataset(
            source_system="datalake",
            source_uri=cleaned_full_path,
            row_count=input_row_count,
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            metadata={"datalake_layer": DatalakeLayer.CLEANED.value}
        )

        enriched_dataframe = self.dataset.processors["inmemory"].enrich(dataframe)
        self.enriched_row_count = len(enriched_dataframe)

        relative_path = generate_relative_path(DatalakeLayer.ENRICHED, self.ingestion_time)
        enriched_full_path = generate_full_path(self.dataset.datalake.bucket_name, relative_path)

        metrics.input_row_count = input_row_count
        metrics.output_row_count = self.enriched_row_count
        metrics.source_system = "datalake"
        metrics.source_uri = cleaned_full_path
        metrics.destination_system = "datalake"
        metrics.destination_uri = enriched_full_path

        inmemory_datalake_service.upload(
            df=enriched_dataframe,
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=relative_path
        )

        self.audit_service.write_dataset(
            source_system="datalake",
            source_uri=cleaned_full_path,
            destination_system="datalake",
            destination_uri=enriched_full_path,
            row_count=self.enriched_row_count,
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            metadata={"datalake_layer": DatalakeLayer.ENRICHED.value}
        )

        self.audit_service.complete_task(context, started_at)

        return relative_path

    def populate_database(self, enriched_data_path: str) -> None:
        metrics = AuditMetrics()

        context, started_at = self.audit_service.start_task(
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            task_name="populate_database",
            task_attempt=self.task_attempt,
            metrics=metrics
        )

        enriched_dataframe = inmemory_datalake_service.download(
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=enriched_data_path
        )

        full_path = generate_full_path(self.dataset.datalake.bucket_name, enriched_data_path)
        row_count = len(enriched_dataframe)

        self.audit_service.read_dataset(
            source_system="datalake",
            source_uri=full_path,
            row_count=row_count,
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            metadata={"datalake_layer": DatalakeLayer.ENRICHED.value}
        )

        metrics.input_row_count = row_count
        metrics.output_row_count = row_count
        metrics.source_system = "datalake"
        metrics.source_uri = full_path
        metrics.destination_system = "postgresql"
        metrics.destination_uri = ec.DATABASE_STAGE_TABLE_NAME

        logger.info("Populating operational database with enriched data")
        database_sale_service.populate(enriched_dataframe)

        self.audit_service.complete_task(context, started_at)

    def populate_datawarehouse(self, enriched_data_path: str) -> None:
        metrics = AuditMetrics()

        context, started_at = self.audit_service.start_task(
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            task_name="populate_datawarehouse",
            task_attempt=self.task_attempt,
            metrics=metrics
        )

        enriched_dataframe = inmemory_datalake_service.download(
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=enriched_data_path
        )

        full_path = generate_full_path(self.dataset.datalake.bucket_name, enriched_data_path)
        row_count = len(enriched_dataframe)

        self.audit_service.read_dataset(
            source_system="datalake",
            source_uri=full_path,
            row_count=row_count,
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            metadata={"datalake_layer": DatalakeLayer.ENRICHED.value}
        )

        metrics.input_row_count = row_count
        metrics.output_row_count = row_count
        metrics.source_system = "datalake"
        metrics.source_uri = full_path
        metrics.destination_system = "datawarehouse"
        metrics.destination_uri = ec.DATAWAREHOUSE_NAME

        logger.info("Populating data warehouse with enriched data")
        datawarehouse_sale_service.truncate_and_populate(self.dataset.datawarehouse, enriched_dataframe)

        self.audit_service.complete_task(context, started_at)

    def analyzing_via_memory(self, enriched_data_path: str) -> None:
        metrics = AuditMetrics()

        context, started_at = self.audit_service.start_task(
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            task_name="analyzing_via_memory",
            task_attempt=self.task_attempt,
            metrics=metrics
        )

        enriched_dataframe = inmemory_datalake_service.download(
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=enriched_data_path
        )

        full_path = generate_full_path(self.dataset.datalake.bucket_name, enriched_data_path)

        self.audit_service.read_dataset(
            source_system="datalake",
            source_uri=full_path,
            row_count=len(enriched_dataframe),
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            metadata={"datalake_layer": DatalakeLayer.ENRICHED.value}
        )

        logger.info("Analyzing enriched data via memory")
        results = self.dataset.processors["inmemory"].analyze(enriched_dataframe)

        metrics.input_row_count = len(enriched_dataframe)
        metrics.output_row_count = sum(len(result) for result in results.values())
        metrics.source_system = "datalake"
        metrics.source_uri = full_path

        show_map_of_dataframe(results)

        self.audit_service.complete_task(context, started_at)

    def analyzing_via_datawarehouse(self) -> None:
        metrics = AuditMetrics()

        context, started_at = self.audit_service.start_task(
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            task_name="analyzing_via_datawarehouse",
            task_attempt=self.task_attempt,
            metrics=metrics
        )

        logger.info("Analyzing enriched data via data warehouse")
        results = datawarehouse_sale_service.analyze(self.dataset.datawarehouse)

        metrics.source_system = "datawarehouse"
        metrics.source_uri = ec.DATAWAREHOUSE_NAME
        metrics.output_row_count = sum(len(result) for result in results.values())

        show_map_of_dataframe(results)

        self.audit_service.complete_task(context, started_at)

    def show_dataframe(self, enriched_data_path: str) -> None:
        enriched_dataframe = inmemory_datalake_service.download(
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=enriched_data_path
        )

        full_path = generate_full_path(self.dataset.datalake.bucket_name, enriched_data_path)

        self.audit_service.read_dataset(
            source_system="datalake",
            source_uri=full_path,
            row_count=len(enriched_dataframe),
            pipeline_name=self.pipeline_name,
            pipeline_id=self.pipeline_id,
            metadata={"datalake_layer": DatalakeLayer.ENRICHED.value}
        )

        logger.info("Displaying enriched data")
        show(enriched_dataframe)
        log_line()