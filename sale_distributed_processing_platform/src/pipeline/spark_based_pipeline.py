import logging
from datetime import UTC, datetime

from itables import show
from pyspark.sql import SparkSession

from app_config import env_config as ec
from app_config.dataframe_schema import SCHEMA
from factory import data_processor_connection_factory
from service import spark_sale_service
from service.datawarehouse import datawarehouse_sale_service
from service.database import database_sale_service
from service.datalake import datalake_spark_sale_service
from util.datalake_utils import DatalakeLayer, build_datalake_path

logger = logging.getLogger(__name__)


def run() -> None:
    session = data_processor_connection_factory.create_connection()
    ingestion_time = datetime.now(UTC)

    try:
        draw_line()
        logger.info("Starting Spark sale pipeline with ingestion time %s", ingestion_time)

        raw_sale_data_path = upload_raw_sale_data(session, ingestion_time)
        draw_line()

        cleaned_sale_data_path = clean_sale_data(session, raw_sale_data_path, ingestion_time)
        draw_line()

        enriched_sale_data_path = enrich_sale_data(session, cleaned_sale_data_path, ingestion_time)
        draw_line()

        populate_database(session, enriched_sale_data_path)
        draw_line()

        populate_datawarehouse(session, enriched_sale_data_path)
        draw_line()

        show_enriched_sale_data(session, enriched_sale_data_path)
        draw_line()

        calculate_revenue_by_category_with_spark(session, enriched_sale_data_path)
        draw_line()

        calculate_revenue_by_country_with_spark(session, enriched_sale_data_path)
        draw_line()

        calculate_revenue_by_category_with_datawarehouse()
        draw_line()

        calculate_revenue_by_country_with_datawarehouse()
        draw_line()
    finally:
        stop_session(session)
        draw_line()


def upload_raw_sale_data(session: SparkSession, ingestion_time: datetime) -> str:
    raw_sale_data_path = build_datalake_path(layer=DatalakeLayer.RAW, ingestion_time=ingestion_time)

    logger.info("Reading sale data from %s", ec.DATA_FILE)
    dataframe = spark_sale_service.read_data(session=session, file_name=ec.DATA_FILE, schema=SCHEMA)

    logger.info("Uploading raw sale data to %s", raw_sale_data_path)
    datalake_spark_sale_service.overwrite(dataframe=dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=raw_sale_data_path)

    return raw_sale_data_path


def clean_sale_data(session: SparkSession, raw_sale_data_path: str, ingestion_time: datetime) -> str:
    cleaned_sale_data_path = build_datalake_path(layer=DatalakeLayer.CLEANED, ingestion_time=ingestion_time)

    logger.info("Reading raw sale data from %s", raw_sale_data_path)
    dataframe = datalake_spark_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=raw_sale_data_path)

    logger.info("Cleaning sale data")
    cleaned_dataframe = spark_sale_service.clean_data(dataframe)

    logger.info("Uploading cleaned sale data to %s", cleaned_sale_data_path)
    datalake_spark_sale_service.overwrite(dataframe=cleaned_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=cleaned_sale_data_path)

    return cleaned_sale_data_path


def enrich_sale_data(session: SparkSession, cleaned_sale_data_path: str, ingestion_time: datetime) -> str:
    enriched_sale_data_path = build_datalake_path(layer=DatalakeLayer.ENRICHED, ingestion_time=ingestion_time)

    logger.info("Reading cleaned sale data from %s", cleaned_sale_data_path)
    dataframe = datalake_spark_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=cleaned_sale_data_path)

    logger.info("Enriching sale data")
    enriched_dataframe = spark_sale_service.enrich_data(dataframe)

    logger.info("Uploading enriched sale data to %s", enriched_sale_data_path)
    datalake_spark_sale_service.overwrite(dataframe=enriched_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_sale_data_path)

    return enriched_sale_data_path


def populate_database(session: SparkSession, enriched_sale_data_path: str) -> None:
    logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
    enriched_dataframe = datalake_spark_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_sale_data_path)

    logger.info("Populating database")
    database_sale_service.populate(enriched_dataframe)


def populate_datawarehouse(session: SparkSession, enriched_sale_data_path: str) -> None:
    logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
    enriched_dataframe = datalake_spark_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_sale_data_path)

    logger.info("Populating datawarehouse")
    datawarehouse_sale_service.populate(enriched_dataframe.toPandas())


def show_enriched_sale_data(session: SparkSession, enriched_sale_data_path: str) -> None:
    logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
    enriched_dataframe = datalake_spark_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_sale_data_path)

    logger.info("Showing enriched sale data")
    enriched_dataframe.show(10)


def calculate_revenue_by_category_with_spark(session: SparkSession, enriched_sale_data_path: str) -> None:
    logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
    enriched_dataframe = datalake_spark_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_sale_data_path)

    logger.info("Calculating revenue by category with Spark")
    revenue_by_category_dataframe = spark_sale_service.get_revenue_by_category(enriched_dataframe)
    revenue_by_category_dataframe.show()


def calculate_revenue_by_country_with_spark(session: SparkSession, enriched_sale_data_path: str) -> None:
    logger.info("Reading enriched sale data from %s", enriched_sale_data_path)
    enriched_dataframe = datalake_spark_sale_service.read(session=session, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_sale_data_path)

    logger.info("Calculating revenue by country with Spark")
    revenue_by_country_dataframe = spark_sale_service.get_revenue_by_country(enriched_dataframe)
    revenue_by_country_dataframe.show()


def calculate_revenue_by_category_with_datawarehouse() -> None:
    logger.info("Calculating revenue by category with Datawarehouse")
    revenue_by_category_dataframe = datawarehouse_sale_service.get_revenue_by_category()
    show(revenue_by_category_dataframe)


def calculate_revenue_by_country_with_datawarehouse() -> None:
    logger.info("Calculating revenue by country with Datawarehouse")
    revenue_by_country_dataframe = datawarehouse_sale_service.get_revenue_by_country()
    show(revenue_by_country_dataframe)


def stop_session(session: SparkSession) -> None:
    logger.info("Stopping Spark session")
    session.stop()


def draw_line() -> None:
    logger.info(100 * "=")
