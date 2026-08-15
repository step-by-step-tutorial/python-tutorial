import logging
from datetime import datetime

import pandas as pd

from app_config import env_config as ec
from dataset.definition import Dataset
from persistence.database import database_service
from persistence.datalake import datalake_service as inmemory_datalake_service
from persistence.datalake.path_utils import DatalakeLayer, generate_relative_path
from persistence.datawarehouse import datawarehouse_service
from presentation.dataframe_display import show
from presentation.dataframe_display import show_map_of_dataframe
from transformation.validation.schema_validator import require_columns
from util.csv_utils import csv_to_dataframe
from util.file_utils import generate_full_file_path
from util.log_utils import log_line
from util.pipeline_utils import create_pipeline_id
from util.time_utils import generate_ingestion_time

logger = logging.getLogger(__name__)


class InmemoryPipeline:

    def __init__(self, ds: Dataset) -> None:
        self.dataset = ds
        self.pipeline_name = "inmemory_pipeline"
        self.pipeline_id = create_pipeline_id()
        self.ingestion_time: datetime = generate_ingestion_time()

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
        self.analyzing_via_memory(enriched_data_path)
        log_line()

        logger.info("step 8")
        self.analyzing_via_datawarehouse()
        log_line()

        logger.info(
            f"Finished ETL pipeline {self.pipeline_name}/{self.pipeline_id} "
            f"with dataset {self.dataset.name} "
            f"at ingestion time {self.ingestion_time.isoformat()}"
        )

    def store_raw_data(self) -> str:
        data_file_path = self.dataset.source.file.resolve_path(generate_full_file_path(ec.RESOURCES_DIR))
        dataframe = csv_to_dataframe(data_file_path)
        require_columns(dataframe, self.dataset.dataframe.required_columns)

        relative_path = generate_relative_path(DatalakeLayer.RAW, self.ingestion_time, self.dataset.name.lower())
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

        relative_path = generate_relative_path(DatalakeLayer.CLEANED, self.ingestion_time, self.dataset.name.lower())
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

        relative_path = generate_relative_path(DatalakeLayer.ENRICHED, self.ingestion_time, self.dataset.name.lower())
        inmemory_datalake_service.upload(
            df=enriched_dataframe,
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=relative_path
        )

        return relative_path

    def download_enriched_data(self, relative_path: str) -> pd.DataFrame:
        return inmemory_datalake_service.download(
            bucket_name=self.dataset.datalake.bucket_name,
            relative_path=relative_path
        )

    def populate_database(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating operational database with enriched data")
        database_service.populate(self.dataset, enriched_dataframe)

    def populate_datawarehouse(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating data warehouse with enriched data")
        datawarehouse_service.truncate_and_populate(self.dataset.datawarehouse, enriched_dataframe)

    def analyzing_via_memory(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Analyzing enriched data via memory")
        results = self.dataset.processors["inmemory"].analyze(enriched_dataframe)
        show_map_of_dataframe(results)

    def analyzing_via_datawarehouse(self):
        result = datawarehouse_service.analyze(self.dataset.datawarehouse)
        logger.info("Analyzing enriched data via data warehouse")
        show_map_of_dataframe(result)

    def show_dataframe(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Displaying enriched data")
        show(enriched_dataframe)
        log_line()
