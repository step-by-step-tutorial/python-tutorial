import logging

from pyspark.sql import DataFrame

from app_config import env_config as ec
from app_config.sale_schema import SCHEMA
from service import sale_bigdata_service
from service import sale_database_service
from service import sale_datalake_service
from service import sale_datawarehouse_service
from util.clean_sale_data_util import clean_sale_data
from util.sale_data_transform_util import transform_sale_data

logger = logging.getLogger(__name__)


class SaleDataPipeline:

    def run(self) -> None:
        dataframe: DataFrame | None = None

        try:
            logger.info("Reading sale data from %s", ec.RAW_SALE_DATA_FILE_PATH)
            dataframe = sale_bigdata_service.read_sale_data(path=ec.RAW_SALE_DATA_FILE_PATH, schema=SCHEMA)

            logger.info("Cleaning sale data")
            cleaned_dataframe = clean_sale_data(dataframe)

            logger.info("Transforming sale data")
            transformed_dataframe = transform_sale_data(cleaned_dataframe)
            transformed_dataframe.cache()

            logger.info("Storing sale data in PostgreSQL")
            sale_database_service.populate(transformed_dataframe)

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
            if dataframe:
                dataframe.unpersist()



