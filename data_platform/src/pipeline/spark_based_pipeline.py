import logging
from datetime import datetime

from pyspark.sql import DataFrame

from audit.audit_service import AuditService
from config.app import settings as app_settings
from config.datalake import settings as datalake_settings
from service.spark.batch_service import SparkBatchService as SparkService
from dataset.definition import Dataset
from persistence.database import database_service
from persistence.datalake.path_utils import DatalakeEnv, generate_relative_path
from persistence.datawarehouse import datawarehouse_service
from presentation.dataframe_display import show
from presentation.dataframe_display import show_map_of_dataframe
from pipeline.batch_pipeline import BatchPipeline

logger = logging.getLogger(__name__)


class SparkPipeline(BatchPipeline):

    def __init__(self, ds: Dataset, audit_service: AuditService | None = None) -> None:
        super().__init__(ds, audit_service=audit_service)
        self.pipeline_name = "spark_pipeline"
        self.spark = SparkService()

    def store_raw_data(self) -> str:
        file_endpoint = self.dataset.get_source("file")
        data_file_path = file_endpoint.resolve_path(app_settings.resources_dir)

        dataframe = self.spark.read_csv(file_path=str(data_file_path), schema=self.dataset.dataframe.schema)

        relative_path = generate_relative_path(DatalakeEnv.RAW, self.ingestion_time, self.dataset.name.lower())

        self.spark.overwrite(
            dataframe=dataframe,
            bucket_name=datalake_settings.bucket_name,
            path=relative_path,
            scheme=datalake_settings.scheme,
        )

        return relative_path

    def cleaning(self, raw_relative_path: str) -> str:
        dataframe = self.spark.read(
            bucket_name=datalake_settings.bucket_name,
            path=raw_relative_path,
            scheme=datalake_settings.scheme,
        )

        cleaned_dataframe = self.dataset.get_processor("spark").clean(dataframe)

        relative_path = generate_relative_path(DatalakeEnv.CLEANED, self.ingestion_time, self.dataset.name.lower())

        self.spark.overwrite(
            dataframe=cleaned_dataframe,
            bucket_name=datalake_settings.bucket_name,
            path=relative_path,
            scheme=datalake_settings.scheme,
        )

        return relative_path

    def enriching(self, cleaned_relative_path: str) -> str:
        dataframe = self.spark.read(
            bucket_name=datalake_settings.bucket_name,
            path=cleaned_relative_path,
            scheme=datalake_settings.scheme,
        )

        enriched_dataframe = self.dataset.get_processor("spark").enrich(dataframe)

        relative_path = generate_relative_path(DatalakeEnv.ENRICHED, self.ingestion_time, self.dataset.name.lower())

        self.spark.overwrite(
            dataframe=enriched_dataframe,
            bucket_name=datalake_settings.bucket_name,
            path=relative_path,
            scheme=datalake_settings.scheme,
        )

        return relative_path

    def download_enriched_data(self, relative_path: str) -> DataFrame:
        return self.spark.read(
            bucket_name=datalake_settings.bucket_name,
            path=relative_path,
            scheme=datalake_settings.scheme,
        )

    def populate_database(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating operational database with enriched data")
        database_service.populate(self.dataset, enriched_dataframe)

    def populate_datawarehouse(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating data warehouse with enriched data")

        datawarehouse_service.truncate_and_populate(
            self.dataset.get_destination("datawarehouse"),
            enriched_dataframe
        )

    def analyzing_via_datawarehouse(self) -> None:
        results = datawarehouse_service.analyze(self.dataset.get_destination("datawarehouse"))
        logger.info("Analyzing enriched data via data warehouse")

        for dataframe in results.values():
            show(dataframe)

    def show_dataframe(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Displaying enriched data")
        enriched_dataframe.show()
        return None

    def analyze_primary(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Analyzing enriched data via Spark")

        results = self.dataset.get_processor("spark").analyze(enriched_dataframe)

        for name, dataframe in results.items():
            logger.info("Displaying analysis result %s", name)
            dataframe.show()

    def after_run(self) -> None:
        self.spark.stop()
