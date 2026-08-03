import logging

from pyspark.sql import DataFrame, SparkSession

from app_config import env_config as ec
from app_config.sale_schema import SCHEMA
from factory import bigdata_engine_session_factory
from service import spark_sale_service
from service import database_sale_service
from service import sale_datalake_service
from service import sale_datawarehouse_service
from util.clean_sale_data_util import clean_sale_data

logger = logging.getLogger(__name__)


def run() -> None:
    spark_session: SparkSession | None = None
    dataframe: DataFrame | None = None

    try:
        spark_session = bigdata_engine_session_factory.create_session()
        logger.info("Reading sale data from %s", ec.DATA_FILE)
        dataframe = spark_sale_service.read_sale_data_from_csv(
            connection=spark_session,
            path=ec.DATA_FILE,
            schema=SCHEMA
        )

        logger.info("Cleaning sale data")
        cleaned_dataframe = clean_sale_data(dataframe)

        logger.info("Transforming sale data")
        transformed_dataframe = spark_sale_service.transform_sale_data(cleaned_dataframe)
        transformed_dataframe.cache()

        logger.info("Storing sale data in PostgreSQL")
        database_sale_service.populate(transformed_dataframe)

        logger.info("Storing curated sale data in datalake")
        sale_datalake_service.overwrite(transformed_dataframe)

        logger.info("Storing sale fact data in data warehouse")
        ordered_dataframe = transformed_dataframe.orderBy("order_id")
        pandas_dataframe = ordered_dataframe.toPandas()
        sale_datawarehouse_service.populate(pandas_dataframe)

        logger.info("Revenue by category:\n%s", sale_datawarehouse_service.get_revenue_by_category())
        logger.info("Revenue by country:\n%s", sale_datawarehouse_service.get_revenue_by_country())

        logger.info("Sale ETL pipeline completed successfully")
    finally:
        stop_spark_session(dataframe, spark_session)


def stop_spark_session(dataframe: DataFrame | None, spark_session: SparkSession | None):
    if dataframe:
        dataframe.unpersist()
    if spark_session:
        spark_session.sparkContext.stop()
        logger.info("Spark context stopped")
        spark_session.stop()
        logger.info("Spark session stopped")
