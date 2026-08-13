import logging
from datetime import datetime

from itables import show
from pyspark.sql import DataFrame

from app_config import env_config as ec
from dataset.definition import Dataset
from service.database import database_sale_service
from service.datawarehouse import datawarehouse_sale_service
from service.spark_service import SparkService
from util.datalake_utils import DatalakeLayer, generate_relative_path
from util.file_utils import generate_full_file_path
from util.log_utils import log_line
from util.pipeline_utils import create_pipeline_id
from util.time_utils import generate_ingestion_time

logger = logging.getLogger(__name__)


class SparkPipeline:

    def __init__(self, ds: Dataset) -> None:
        self.dataset = ds
        self.pipeline_name = "spark_pipeline"
        self.pipeline_id = create_pipeline_id()
        self.ingestion_time: datetime = generate_ingestion_time()
        self.spark = SparkService(ds)

    def run(self) -> None:
        logger.info(
            f"Starting ETL pipeline {self.pipeline_name}/{self.pipeline_id} "
            f"with dataset {self.dataset.name} "
            f"at ingestion time {self.ingestion_time.isoformat()}"
        )
        log_line()

        logger.info("step 1")
        raw_relative_path = self.store_raw_data()
        log_line()

        logger.info("step 2")
        cleaned_data_path = self.cleaning(raw_relative_path)
        log_line()

        logger.info("step 3")
        enriched_data_path = self.enriching(cleaned_data_path)
        log_line()

        logger.info("step 4")
        self.populate_database(enriched_data_path)
        log_line()

        logger.info("step 5")
        self.populate_datawarehouse(enriched_data_path)
        log_line()

        logger.info("step 6")
        self.show_dataframe(enriched_data_path)

        logger.info("step 7")
        self.analyzing_via_spark(enriched_data_path)
        log_line()

        logger.info("step 8")
        self.analyzing_via_datawarehouse()
        log_line()

        logger.info(
            f"Finished ETL pipeline {self.pipeline_name}/{self.pipeline_id} "
            f"with dataset {self.dataset.name} "
            f"at ingestion time {self.ingestion_time.isoformat()}"
        )

        self.spark.stop()

    def store_raw_data(self) -> str:
        data_file_path = generate_full_file_path(ec.RESOURCES_DIR) / self.dataset.file_name

        dataframe = self.spark.read_csv(
            file_path=str(data_file_path),
            schema=self.dataset.dataframe_schema,
            required_columns=self.dataset.required_columns
        )

        relative_path = generate_relative_path(DatalakeLayer.RAW, self.ingestion_time)

        self.spark.overwrite(
            dataframe=dataframe,
            bucket_name=self.dataset.datalake.bucket_name,
            path=relative_path
        )

        return relative_path

    def cleaning(self, raw_relative_path: str) -> str:
        dataframe = self.spark.read(
            bucket_name=self.dataset.datalake.bucket_name,
            path=raw_relative_path
        )

        cleaned_dataframe = self.dataset.processors["spark"].clean(dataframe)

        relative_path = generate_relative_path(DatalakeLayer.CLEANED, self.ingestion_time)

        self.spark.overwrite(
            dataframe=cleaned_dataframe,
            bucket_name=self.dataset.datalake.bucket_name,
            path=relative_path
        )

        return relative_path

    def enriching(self, cleaned_relative_path: str) -> str:
        dataframe = self.spark.read(
            bucket_name=self.dataset.datalake.bucket_name,
            path=cleaned_relative_path
        )

        enriched_dataframe = self.dataset.processors["spark"].enrich(dataframe)

        relative_path = generate_relative_path(DatalakeLayer.ENRICHED, self.ingestion_time)

        self.spark.overwrite(
            dataframe=enriched_dataframe,
            bucket_name=self.dataset.datalake.bucket_name,
            path=relative_path
        )

        return relative_path

    def download_enriched_data(self, relative_path: str) -> DataFrame:
        return self.spark.read(
            bucket_name=self.dataset.datalake.bucket_name,
            path=relative_path
        )

    def populate_database(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating operational database with enriched data")
        database_sale_service.populate(enriched_dataframe)

    def populate_datawarehouse(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating data warehouse with enriched data")

        datawarehouse_sale_service.truncate_and_populate(
            self.dataset.datawarehouse,
            enriched_dataframe.toPandas()
        )

    def analyzing_via_spark(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Analyzing enriched data via Spark")

        results = self.dataset.processors["spark"].analyze(enriched_dataframe)

        for name, dataframe in results.items():
            logger.info("Displaying analysis result %s", name)
            dataframe.show()

    def analyzing_via_datawarehouse(self) -> None:
        results = datawarehouse_sale_service.analyze(self.dataset.datawarehouse)
        logger.info("Analyzing enriched data via data warehouse")

        for dataframe in results.values():
            show(dataframe)

    def show_dataframe(self, enriched_data_path: str) -> None:
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Displaying enriched data")
        enriched_dataframe.show()
        log_line()
