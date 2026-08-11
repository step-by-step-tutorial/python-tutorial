import logging
from datetime import UTC, datetime
from typing import Mapping

import pandas as pd
from itables import show
from pandas import DataFrame

from app_config import env_config as ec
from dataset.definition import Dataset
from service.database import database_sale_service
from service.datalake import inmemory_datalake_service
from service.datawarehouse import datawarehouse_sale_service
from util.csv_utils import csv_to_dataframe
from util.datalake_utils import DatalakeLayer, generate_relative_path
from util.file_utils import absolute_path
from util.log_utils import log_line
from util.pandas_dataframe_utils import require_columns, show_map_of_dataframe

logger = logging.getLogger(__name__)


class InmemoryPipeline:

    def __init__(self, ds: Dataset) -> None:
        self.dataset = ds
        self.ingestion_time: datetime = datetime.now(UTC)
        self.run()

    def run(self) -> None:
        logger.info("Starting ETL pipeline with dataset %s at ingestion time %s", self.dataset.name, self.ingestion_time)
        log_line()

        raw_relative_path = self.store_raw_data()
        log_line()

        cleaned_data_path = self.cleaning(raw_relative_path)
        log_line()

        enriched_data_path = self.enriching(cleaned_data_path)
        log_line()

        enriched_dataframe = self.download_enriched_data(enriched_data_path)

        logger.info("Displaying enriched data")
        show(enriched_dataframe)

        logger.info("Populating operational database with enriched data")
        database_sale_service.populate(enriched_dataframe)
        log_line()

        logger.info("Populating data warehouse with enriched data")
        datawarehouse_sale_service.populate(enriched_dataframe)
        log_line()

        analysis_results = self.analyzing(enriched_dataframe)
        show_map_of_dataframe(analysis_results)
        log_line()

        self.show_revenue_by_datawarehouse()
        log_line()

        logger.info("Finished ETL pipeline with dataset %s at ingestion time %s", self.dataset.name, self.ingestion_time)

    def store_raw_data(self) -> str:
        dataframe = csv_to_dataframe(absolute_path(ec.RESOURCES_DIR) / self.dataset.file_name)
        require_columns(dataframe, self.dataset.required_columns)

        relative_path = generate_relative_path(DatalakeLayer.RAW, self.ingestion_time)
        inmemory_datalake_service.upload(
            df=dataframe,
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=relative_path
        )

        return relative_path

    def cleaning(self, raw_relative_path: str) -> str:
        dataframe = inmemory_datalake_service.download(
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=raw_relative_path
        )

        cleaned_dataframe = self.dataset.processors["inmemory"].clean(dataframe)

        relative_path = generate_relative_path(DatalakeLayer.CLEANED, self.ingestion_time)
        inmemory_datalake_service.upload(
            df=cleaned_dataframe,
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=relative_path
        )

        return relative_path

    def enriching(self, cleaned_relative_path: str) -> str:
        dataframe = inmemory_datalake_service.download(
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=cleaned_relative_path
        )
        enriched_dataframe = self.dataset.processors["inmemory"].enrich(dataframe)

        relative_path = generate_relative_path(DatalakeLayer.ENRICHED, self.ingestion_time)
        inmemory_datalake_service.upload(
            df=enriched_dataframe,
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=relative_path
        )

        return relative_path

    def download_enriched_data(self, relative_path: str) -> pd.DataFrame:
        return inmemory_datalake_service.download(bucket_name=self.dataset.datalake.bucket_name,
                                                  relative_path=relative_path)

    def analyzing(self, dataframe: pd.DataFrame) -> Mapping[str, DataFrame]:
        return self.dataset.processors["inmemory"].analyze(dataframe)

    def show_revenue_by_datawarehouse(self) -> None:
        logger.info("Calculating revenue by category using the data warehouse")
        revenue_by_category = datawarehouse_sale_service.get_revenue_by_category()
        show(revenue_by_category)

        logger.info("Calculating revenue by country using the data warehouse")
        revenue_by_country = datawarehouse_sale_service.get_revenue_by_country()
        show(revenue_by_country)
