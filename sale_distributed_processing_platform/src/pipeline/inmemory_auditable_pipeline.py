import logging
import time
from datetime import UTC, datetime

import pandas as pd
from itables import show

from app_config import env_config as ec
from model.audit_event import AuditEvent, AuditEventType, AuditStatus
from repository import audit_repository
from service import csv_sale_service
from service.audit.audit_pipeline_service import AuditPipelineService
from service.audit.audit_task_service import AuditTaskService
from service.database import database_sale_service
from service.datalake import datalake_pandas_sale_service
from service.datawarehouse import datawarehouse_sale_service
from streaming.audit_event_producer import AuditEventProducer
from util.datalake_utils import DatalakeLayer, build_datalake_path, build_datalake_uri
from util.log_utils import log_line
from util.pipeline_utils import create_pipeline_id
from util.time_utils import elapsed_milliseconds

logger = logging.getLogger(__name__)

PIPELINE_NAME = "InmemoryAuditablePipeline"
TASK_ATTEMPT = 1


class InmemoryAuditablePipeline:

    def __init__(self) -> None:
        self.ingestion_time: datetime = datetime.now(UTC)
        self.pipeline_id: str = create_pipeline_id()
        self.producer = AuditEventProducer()
        self.audit_pipeline_service = AuditPipelineService()
        self.audit_task_service = AuditTaskService()
        self.run()

    def run(self) -> None:
        started_at = time.perf_counter()

        try:
            pipeline_started_event = self.audit_pipeline_service.pipeline_started(
                pipeline_name=PIPELINE_NAME,
                pipeline_id=self.pipeline_id,
                metadata={"data_file": ec.DATA_FILE},
            )
            audit_repository.save_event(pipeline_started_event, ec.STREAMING_AUDIT_TOPIC)

            log_line()
            logger.info("Starting pipeline with run id %s and ingestion time %s", self.pipeline_id, self.ingestion_time)

            raw_data_path, input_row_count = self.store_raw_data()
            log_line()

            cleaned_data_path, cleaned_row_count, rejected_row_count = self.clean_data(raw_data_path)
            log_line()

            enriched_data_path, output_row_count = self.enrich_data(cleaned_data_path)
            log_line()

            enriched_dataframe = self.read_enriched_data(enriched_data_path)

            self.populate_database(enriched_dataframe)
            log_line()

            self.populate_datawarehouse(enriched_dataframe)
            log_line()

            self.show_revenue_by_pandas(enriched_dataframe)
            log_line()

            self.show_revenue_by_datawarehouse()
            log_line()

            self.audit_pipeline_service.pipeline_completed(
                pipeline_name=PIPELINE_NAME,
                pipeline_id=self.pipeline_id,
                input_row_count=input_row_count,
                output_row_count=output_row_count,
                rejected_row_count=rejected_row_count,
                duration_ms=elapsed_milliseconds(started_at),
                metadata={
                    "raw_path": raw_data_path,
                    "cleaned_path": cleaned_data_path,
                    "enriched_path": enriched_data_path,
                    "cleaned_row_count": cleaned_row_count,
                },
            )

            logger.info("Pipeline completed successfully with run id %s", self.pipeline_id)

        except Exception as error:
            self.audit_pipeline_service.pipeline_failed(
                pipeline_name=PIPELINE_NAME,
                pipeline_id=self.pipeline_id,
                error=error,
                duration_ms=elapsed_milliseconds(started_at),
            )
            raise

        finally:
            self.flush_producers()
            log_line()

    def store_raw_data(self) -> tuple[str, int]:
        path = build_datalake_path(DatalakeLayer.RAW, self.ingestion_time)

        with self.audit_task_service.audit_task(PIPELINE_NAME, self.pipeline_id, "store_raw_data",
                                                TASK_ATTEMPT) as metrics:
            logger.info("Reading data from file %s", ec.DATA_FILE)
            dataframe = csv_sale_service.read_data(ec.DATA_FILE)

            row_count = len(dataframe)

            metrics.input_row_count = row_count
            metrics.output_row_count = row_count
            metrics.source_system = "csv"
            metrics.source_uri = ec.DATA_FILE
            metrics.destination_system = "datalake"
            metrics.destination_uri = build_datalake_uri(path)

            logger.info("Storing raw data in datalake path %s", path)
            datalake_pandas_sale_service.upload_parquet(dataframe, ec.DATALAKE_BUCKET_NAME, path)

        self.publish_written_event(
            source="csv",
            source_uri=ec.DATA_FILE,
            destination_uri=path,
            row_count=row_count,
            layer=DatalakeLayer.RAW,
        )

        return path, row_count

    def clean_data(self, raw_data_path: str) -> tuple[str, int, int]:
        cleaned_data_path = build_datalake_path(DatalakeLayer.CLEANED, self.ingestion_time)

        with self.audit_task_service.audit_task(PIPELINE_NAME, self.pipeline_id, "clean_data", TASK_ATTEMPT) as metrics:
            logger.info("Reading raw data from datalake path %s", raw_data_path)
            raw_dataframe = datalake_pandas_sale_service.download_parquet(ec.DATALAKE_BUCKET_NAME, raw_data_path)

            input_row_count = len(raw_dataframe)

            metrics.input_row_count = input_row_count
            metrics.source_system = "datalake"
            metrics.source_uri = build_datalake_uri(raw_data_path)

            logger.info("Cleaning data")
            cleaned_dataframe = csv_sale_service.clean_data(raw_dataframe)

            output_row_count = len(cleaned_dataframe)
            rejected_row_count = input_row_count - output_row_count

            metrics.output_row_count = output_row_count
            metrics.rejected_row_count = rejected_row_count
            metrics.destination_system = "datalake"
            metrics.destination_uri = build_datalake_uri(cleaned_data_path)

            logger.info("Storing cleaned data in datalake path %s", cleaned_data_path)
            datalake_pandas_sale_service.upload_parquet(cleaned_dataframe, ec.DATALAKE_BUCKET_NAME, cleaned_data_path)

        self.publish_written_event(
            source="datalake",
            source_uri=build_datalake_uri(raw_data_path),
            destination_uri=cleaned_data_path,
            row_count=output_row_count,
            layer=DatalakeLayer.CLEANED,
        )

        return cleaned_data_path, output_row_count, rejected_row_count

    def enrich_data(self, cleaned_data_path: str) -> tuple[str, int]:
        enriched_data_path = build_datalake_path(DatalakeLayer.ENRICHED, self.ingestion_time)

        with self.audit_task_service.audit_task(PIPELINE_NAME, self.pipeline_id, "enrich_data",
                                                TASK_ATTEMPT) as metrics:
            logger.info("Reading cleaned data from datalake path %s", cleaned_data_path)
            cleaned_dataframe = datalake_pandas_sale_service.download_parquet(ec.DATALAKE_BUCKET_NAME,
                                                                              cleaned_data_path)

            input_row_count = len(cleaned_dataframe)

            metrics.input_row_count = input_row_count
            metrics.source_system = "datalake"
            metrics.source_uri = build_datalake_uri(cleaned_data_path)

            logger.info("Enriching data")
            enriched_dataframe = csv_sale_service.enrich_data(cleaned_dataframe)

            output_row_count = len(enriched_dataframe)

            metrics.output_row_count = output_row_count
            metrics.destination_system = "datalake"
            metrics.destination_uri = build_datalake_uri(enriched_data_path)

            logger.info("Storing enriched data in datalake path %s", enriched_data_path)
            datalake_pandas_sale_service.upload_parquet(enriched_dataframe, ec.DATALAKE_BUCKET_NAME, enriched_data_path)

        self.publish_written_event(
            source="datalake",
            source_uri=build_datalake_uri(cleaned_data_path),
            destination_uri=enriched_data_path,
            row_count=output_row_count,
            layer=DatalakeLayer.ENRICHED,
        )

        return enriched_data_path, output_row_count

    def read_enriched_data(self, enriched_data_path: str) -> pd.DataFrame:
        with self.audit_task_service.audit_task(PIPELINE_NAME, self.pipeline_id, "read_enriched_data",
                                                TASK_ATTEMPT) as metrics:
            logger.info("Reading enriched data from datalake path %s", enriched_data_path)
            dataframe = datalake_pandas_sale_service.download_parquet(ec.DATALAKE_BUCKET_NAME, enriched_data_path)

            row_count = len(dataframe)

            metrics.input_row_count = row_count
            metrics.output_row_count = row_count
            metrics.source_system = "datalake"
            metrics.source_uri = build_datalake_uri(enriched_data_path)

        self.publish_read_event(enriched_data_path, row_count)

        return dataframe

    def populate_database(self, dataframe: pd.DataFrame) -> None:
        with self.audit_task_service.audit_task(PIPELINE_NAME, self.pipeline_id, "populate_database",
                                                TASK_ATTEMPT) as metrics:
            row_count = len(dataframe)

            metrics.input_row_count = row_count
            metrics.output_row_count = row_count
            metrics.source_system = "dataframe"
            metrics.source_uri = "enriched_dataframe"
            metrics.destination_system = "postgresql"
            metrics.destination_uri = ec.DATABASE_STAGE_TABLE_NAME

            logger.info("Populating operational database with enriched data")
            database_sale_service.populate(dataframe)

    def populate_datawarehouse(self, dataframe: pd.DataFrame) -> None:
        with self.audit_task_service.audit_task(PIPELINE_NAME, self.pipeline_id, "populate_datawarehouse",
                                                TASK_ATTEMPT) as metrics:
            row_count = len(dataframe)

            metrics.input_row_count = row_count
            metrics.output_row_count = row_count
            metrics.source_system = "dataframe"
            metrics.source_uri = "enriched_dataframe"
            metrics.destination_system = "clickhouse"
            metrics.destination_uri = ec.DATAWAREHOUSE_NAME

            logger.info("Populating data warehouse with enriched data")
            datawarehouse_sale_service.populate(dataframe)

    def show_revenue_by_pandas(self, dataframe: pd.DataFrame) -> None:
        with self.audit_task_service.audit_task(PIPELINE_NAME, self.pipeline_id, "show_revenue_by_pandas",
                                                TASK_ATTEMPT) as metrics:
            metrics.input_row_count = len(dataframe)

            logger.info("Displaying enriched data")
            show(dataframe)

            logger.info("Calculating revenue by category using Pandas")
            revenue_by_category = csv_sale_service.get_revenue_by_category(dataframe)
            show(revenue_by_category)

            logger.info("Calculating revenue by country using Pandas")
            revenue_by_country = csv_sale_service.get_revenue_by_country(dataframe)
            show(revenue_by_country)

            metrics.output_row_count = len(revenue_by_category) + len(revenue_by_country)

    def show_revenue_by_datawarehouse(self) -> None:
        with self.audit_task_service.audit_task(PIPELINE_NAME, self.pipeline_id, "show_revenue_by_datawarehouse",
                                                TASK_ATTEMPT) as metrics:
            logger.info("Calculating revenue by category using the data warehouse")
            revenue_by_category = datawarehouse_sale_service.get_revenue_by_category()
            show(revenue_by_category)

            logger.info("Calculating revenue by country using the data warehouse")
            revenue_by_country = datawarehouse_sale_service.get_revenue_by_country()
            show(revenue_by_country)

            metrics.output_row_count = len(revenue_by_category) + len(revenue_by_country)

    def publish_read_event(self, path: str, row_count: int) -> None:
        self.producer.publish(
            AuditEvent(
                event_type=AuditEventType.DATASET_READ,
                pipeline_name=PIPELINE_NAME,
                pipeline_id=self.pipeline_id,
                status=AuditStatus.SUCCEEDED,
                source_system="datalake",
                source_uri=build_datalake_uri(path),
                input_row_count=row_count,
            )
        )

    def publish_written_event(self, source: str, source_uri: str, destination_uri: str, row_count: int,
                              layer: str) -> None:
        self.producer.publish(
            AuditEvent(
                event_type=AuditEventType.DATASET_WRITTEN,
                pipeline_name=PIPELINE_NAME,
                pipeline_id=self.pipeline_id,
                status=AuditStatus.SUCCEEDED,
                source_system=source,
                source_uri=source_uri,
                destination_system="datalake",
                destination_uri=build_datalake_uri(destination_uri),
                output_row_count=row_count,
                metadata={"datalake_layer": layer},
            )
        )

    def flush_producers(self) -> None:
        self.producer.flush()
        self.audit_pipeline_service.producer.flush()
        self.audit_task_service.producer.flush()
