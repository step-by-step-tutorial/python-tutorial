import logging
from datetime import datetime
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
from util.time_utils import generate_ingestion_time

logger = logging.getLogger(__name__)


class InmemoryPipeline:

    def __init__(self, ds: Dataset) -> None:
        self.dataset = ds
        self.ingestion_time: datetime = generate_ingestion_time()
        self.run()

    def run(self) -> None:
        logger.info(
            "Starting ETL pipeline with dataset %s at ingestion time %s",
            self.dataset.name,
            self.ingestion_time.isoformat()
        )
        log_line()

        raw_relative_path = self.store_raw_data()
        log_line()

        cleaned_data_path = self.cleaning(raw_relative_path)
        log_line()

        enriched_data_path = self.enriching(cleaned_data_path)
        log_line()

        enriched_dataframe = self.download_enriched_data(enriched_data_path)

        logger.info("Populating operational database with enriched data")
        database_sale_service.populate(enriched_dataframe)
        log_line()

        logger.info("Populating data warehouse with enriched data")
        datawarehouse_sale_service.truncate_and_populate(self.dataset.datawarehouse, enriched_dataframe)
        log_line()

        logger.info("Displaying enriched data")
        show(enriched_dataframe)
        log_line()

        logger.info("Analyzing enriched data via memory")
        analysis_via_memory_results = self.analyzing_via_memory(enriched_dataframe)
        show_map_of_dataframe(analysis_via_memory_results)
        log_line()

        logger.info("Analyzing enriched data via data warehouse")
        analysis_via_datawarehouse_result = self.analyzing_via_datawarehouse()
        show_map_of_dataframe(analysis_via_datawarehouse_result)
        log_line()

        logger.info(
            "Finished ETL pipeline with dataset %s at ingestion time %s",
            self.dataset.name,
            self.ingestion_time.isoformat()
        )

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

    def analyzing_via_memory(self, dataframe: pd.DataFrame) -> Mapping[str, DataFrame]:
        return self.dataset.processors["inmemory"].analyze(dataframe)

    def analyzing_via_datawarehouse(self) -> Mapping[str, DataFrame]:
        return datawarehouse_sale_service.analyze(self.dataset.datawarehouse)
