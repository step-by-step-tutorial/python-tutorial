import logging

from pyspark.sql import DataFrame

from app_config import env_config as ec
from app_config.dataframe_schema import SCHEMA
from factory import data_processor_connection_factory
from service import spark_sale_service, database_sale_service, datawarehouse_sale_service
from itables import show

logger = logging.getLogger(__name__)


def run() -> None:
    session = data_processor_connection_factory.create_connection()

    try:
        draw_line()
        logger.info("Reading sale data from %s", ec.DATA_FILE)
        dataframe = spark_sale_service.read_data(session=session, path=ec.DATA_FILE, schema=SCHEMA)
        draw_line()

        logger.info("Cleaning sale data")
        cleaned_dataframe = spark_sale_service.clean_data(dataframe)
        draw_line()

        logger.info("Enriching sale data")
        enriched_dataframe = spark_sale_service.enrich_data(cleaned_dataframe)
        draw_line()

        logger.info("Populating database")
        database_sale_service.populate(enriched_dataframe)
        draw_line()

        logger.info("Populate datawarehouse")
        datawarehouse_sale_service.populate(enriched_dataframe.toPandas())
        draw_line()

        enriched_dataframe.show(10)
        draw_line()
        process_data_by_spark(enriched_dataframe)
        draw_line()
        process_data_by_datawarehouse()
        draw_line()

    finally:
        logger.info("Stopping Spark session")
        session.stop()
        draw_line()


def process_data_by_spark(enriched_dataframe: DataFrame):
    logger.info("Processing data by Spark")

    logger.info("Calculating revenue by category")
    revenue_by_category_dataframe = spark_sale_service.get_revenue_by_category(enriched_dataframe)
    revenue_by_category_dataframe.show()

    logger.info("Calculating revenue by country")
    revenue_by_country_dataframe = spark_sale_service.get_revenue_by_country(enriched_dataframe)
    revenue_by_country_dataframe.show()


def process_data_by_datawarehouse():
    logger.info("Processing data by Datawarehouse")

    logger.info("Calculating revenue by category")
    revenue_by_category_dataframe = datawarehouse_sale_service.get_revenue_by_category()
    show(revenue_by_category_dataframe)

    logger.info("Calculating revenue by country")
    revenue_by_country_dataframe = datawarehouse_sale_service.get_revenue_by_country()
    show(revenue_by_country_dataframe)


def draw_line():
    logger.info(100 * "=")
