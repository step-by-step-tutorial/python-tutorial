import logging
from datetime import UTC, datetime

from itables import show
from pyspark.sql import DataFrame, SparkSession

from app_config import env_config as ec
from app_config.dataframe_schema import SCHEMA
from factory import spark_connection_factory
from service import spark_sale_service
from service.database import database_sale_service
from service.datalake import distributed_datalake_service
from service.datawarehouse import datawarehouse_sale_service
from util.datalake_utils import DatalakeLayer, generate_relative_path
from util.log_utils import log_line

logger = logging.getLogger(__name__)


class SparkPipeline:

    def __init__(self) -> None:
        self.session: SparkSession = spark_connection_factory.create_connection()
        self.ingestion_time: datetime = datetime.now(UTC)
        self.run()

    def run(self) -> None:
        try:
            log_line()
            logger.info("Starting pipeline with ingestion time %s", self.ingestion_time)

            raw_data_path = self.store_raw_data()
            log_line()

            cleaned_data_path = self.clean_data(raw_data_path)
            log_line()

            enriched_data_path = self.enrich_data(cleaned_data_path)
            log_line()

            enriched_dataframe = self.read_enriched_data(enriched_data_path)

            logger.info("Populating operational database with enriched data")
            database_sale_service.populate(enriched_dataframe)
            log_line()

            logger.info("Populating data warehouse with enriched data")
            datawarehouse_sale_service.populate(enriched_dataframe.toPandas())
            log_line()

            self.show_revenue_by_spark(enriched_dataframe)
            log_line()

            self.show_revenue_by_datawarehouse()
            log_line()

            logger.info("Pipeline completed successfully")
        finally:
            self.stop()
            log_line()

    def store_raw_data(self) -> str:
        raw_data_path = generate_relative_path(DatalakeLayer.RAW, self.ingestion_time)

        logger.info("Reading data from file %s", ec.DATA_FILE)
        dataframe = spark_sale_service.read_data(session=self.session, file_name=ec.DATA_FILE, schema=SCHEMA)

        logger.info("Storing raw data in datalake path %s", raw_data_path)
        distributed_datalake_service.overwrite(dataframe=dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=raw_data_path)

        return raw_data_path

    def clean_data(self, raw_data_path: str) -> str:
        logger.info("Reading raw data from datalake path %s", raw_data_path)
        dataframe = distributed_datalake_service.read(session=self.session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=raw_data_path)

        logger.info("Cleaning data")
        cleaned_dataframe = spark_sale_service.clean_data(dataframe)

        cleaned_data_path = generate_relative_path(DatalakeLayer.CLEANED, self.ingestion_time)
        logger.info("Storing cleaned data in datalake path %s", cleaned_data_path)
        distributed_datalake_service.overwrite(dataframe=cleaned_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=cleaned_data_path)

        return cleaned_data_path

    def enrich_data(self, cleaned_data_path: str) -> str:

        logger.info("Reading cleaned data from datalake path %s", cleaned_data_path)
        dataframe = distributed_datalake_service.read(session=self.session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=cleaned_data_path)

        logger.info("Enriching data")
        enriched_dataframe = spark_sale_service.enrich_data(dataframe)

        enriched_data_path = generate_relative_path(DatalakeLayer.ENRICHED, self.ingestion_time)
        logger.info("Storing enriched data in datalake path %s", enriched_data_path)
        distributed_datalake_service.overwrite(dataframe=enriched_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_data_path)

        return enriched_data_path

    def read_enriched_data(self, enriched_data_path: str) -> DataFrame:
        logger.info("Reading enriched data from datalake path %s", enriched_data_path)
        return distributed_datalake_service.read(session=self.session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_data_path)

    @staticmethod
    def show_revenue_by_spark(dataframe: DataFrame) -> None:
        logger.info("Displaying enriched data sample")
        dataframe.show(10)

        logger.info("Calculating revenue by category using Spark")
        revenue_by_category = spark_sale_service.get_revenue_by_category(dataframe)
        revenue_by_category.show()

        logger.info("Calculating revenue by country using Spark")
        revenue_by_country = spark_sale_service.get_revenue_by_country(dataframe)
        revenue_by_country.show()

    @staticmethod
    def show_revenue_by_datawarehouse() -> None:
        logger.info("Calculating revenue by category using the data warehouse")
        revenue_by_category = datawarehouse_sale_service.get_revenue_by_category()
        show(revenue_by_category)

        logger.info("Calculating revenue by country using the data warehouse")
        revenue_by_country = datawarehouse_sale_service.get_revenue_by_country()
        show(revenue_by_country)

    def stop(self) -> None:
        logger.info("Stopping Spark session")
        self.session.stop()
