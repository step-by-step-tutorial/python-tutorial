import logging

from app_config import env_config as ec
from app_config.sale_schema import SCHEMA
from factory import data_processor_connection_factory
from service import spark_sale_service

logger = logging.getLogger(__name__)


def run() -> None:
    session = data_processor_connection_factory.create_connection()

    try:
        logger.info("Reading sale data from %s", ec.DATA_FILE)
        dataframe = spark_sale_service.read_data(session=session, path=ec.DATA_FILE, schema=SCHEMA)

        logger.info("Cleaning sale data")
        cleaned_dataframe = spark_sale_service.clean_data(dataframe)

        logger.info("Enriching sale data")
        enriched_dataframe = spark_sale_service.enrich_data(cleaned_dataframe)

        logger.info("Calculating revenue by category")
        revenue_by_category_dataframe = spark_sale_service.get_revenue_by_category(enriched_dataframe)

        logger.info("Calculating revenue by country")
        revenue_by_country_dataframe = spark_sale_service.get_revenue_by_country(enriched_dataframe)

        enriched_dataframe.show()
        revenue_by_category_dataframe.show()
        revenue_by_country_dataframe.show()
    finally:
        logger.info("Stopping Spark session")
        session.stop()
