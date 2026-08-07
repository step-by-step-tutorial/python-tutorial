import logging
from datetime import UTC, datetime

import pandas as pd
from itables import show

from app_config import env_config as ec
from service import pandas_sale_service
from service.database import database_sale_service
from service.datalake import datalake_pandas_sale_service
from service.datawarehouse import datawarehouse_sale_service
from util.datalake_utils import DatalakeLayer, build_datalake_path
from util.log_utils import log_line

logger = logging.getLogger(__name__)


class InmemoryPipeline:

    def __init__(self) -> None:
        self.ingestion_time: datetime = datetime.now(UTC)
        self.run()

    def run(self) -> None:
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
        datawarehouse_sale_service.populate(enriched_dataframe)
        log_line()

        self.show_revenue_by_pandas(enriched_dataframe)
        log_line()

        self.show_revenue_by_datawarehouse()
        log_line()

        logger.info("Pipeline completed successfully")

    def store_raw_data(self) -> str:
        raw_data_path = build_datalake_path(DatalakeLayer.RAW, self.ingestion_time)

        logger.info("Reading data from file %s", ec.DATA_FILE)
        dataframe = pandas_sale_service.read_data(file_name=ec.DATA_FILE)

        logger.info("Storing raw data in datalake path %s", raw_data_path)
        datalake_pandas_sale_service.upload_parquet(df=dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=raw_data_path)

        return raw_data_path

    def clean_data(self, raw_data_path: str) -> str:
        logger.info("Reading raw data from datalake path %s", raw_data_path)
        dataframe = datalake_pandas_sale_service.download_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME, path=raw_data_path)

        logger.info("Cleaning data")
        cleaned_dataframe = pandas_sale_service.clean_data(dataframe)

        cleaned_data_path = build_datalake_path(DatalakeLayer.CLEANED, self.ingestion_time)

        logger.info("Storing cleaned data in datalake path %s", cleaned_data_path)
        datalake_pandas_sale_service.upload_parquet(df=cleaned_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=cleaned_data_path)

        return cleaned_data_path

    def enrich_data(self, cleaned_data_path: str) -> str:
        logger.info("Reading cleaned data from datalake path %s", cleaned_data_path)
        dataframe = datalake_pandas_sale_service.download_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME, path=cleaned_data_path)

        logger.info("Enriching data")
        enriched_dataframe = pandas_sale_service.enrich_data(dataframe)

        enriched_data_path = build_datalake_path(DatalakeLayer.ENRICHED, self.ingestion_time)

        logger.info("Storing enriched data in datalake path %s", enriched_data_path)
        datalake_pandas_sale_service.upload_parquet(df=enriched_dataframe, bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_data_path)

        return enriched_data_path

    @staticmethod
    def read_enriched_data(enriched_data_path: str) -> pd.DataFrame:
        logger.info("Reading enriched data from datalake path %s", enriched_data_path)
        return datalake_pandas_sale_service.download_parquet(bucket_name=ec.DATALAKE_BUCKET_NAME, path=enriched_data_path)

    @staticmethod
    def show_revenue_by_pandas(dataframe: pd.DataFrame) -> None:
        logger.info("Displaying enriched data")
        show(dataframe)

        logger.info("Calculating revenue by category using Pandas")
        revenue_by_category = pandas_sale_service.get_revenue_by_category(dataframe)
        show(revenue_by_category)

        logger.info("Calculating revenue by country using Pandas")
        revenue_by_country = pandas_sale_service.get_revenue_by_country(dataframe)
        show(revenue_by_country)

    @staticmethod
    def show_revenue_by_datawarehouse() -> None:
        logger.info("Calculating revenue by category using the data warehouse")
        revenue_by_category = datawarehouse_sale_service.get_revenue_by_category()
        show(revenue_by_category)

        logger.info("Calculating revenue by country using the data warehouse")
        revenue_by_country = datawarehouse_sale_service.get_revenue_by_country()
        show(revenue_by_country)