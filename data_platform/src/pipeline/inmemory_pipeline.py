import logging
from datetime import datetime

import pandas as pd

from config.app import settings as app_settings
from config.datalake import settings as datalake_settings
from audit.audit_service import AuditService
from dataset.definition import Dataset
from persistence.database import database_service
from persistence.datalake import datalake_service as inmemory_datalake_service
from persistence.datalake.path_utils import DatalakeEnv, generate_relative_path
from persistence.datawarehouse import datawarehouse_service
from presentation.dataframe_display import show
from presentation.dataframe_display import show_map_of_dataframe
from pipeline.batch_pipeline import BatchPipeline
from transformation.validation.schema_validator import require_columns
from util.csv_utils import csv_to_dataframe
from util.log_utils import log_line

logger = logging.getLogger(__name__)


class InmemoryPipeline(BatchPipeline):

    def __init__(self, ds: Dataset, audit_service: AuditService | None = None) -> None:
        super().__init__(ds, audit_service=audit_service)
        self.pipeline_name = "inmemory_pipeline"

    def store_raw_data(self) -> str:
        file_endpoint = self.dataset.get_source("file")
        data_file_path = file_endpoint.resolve_path(app_settings.resources_dir)
        dataframe = csv_to_dataframe(data_file_path)
        require_columns(dataframe, self.dataset.dataframe.required_columns)

        relative_path = generate_relative_path(DatalakeEnv.RAW, self.ingestion_time, self.dataset.name.lower())
        inmemory_datalake_service.upload(
            df=dataframe,
            bucket_name=datalake_settings.bucket_name,
            relative_path=relative_path
        )

        return relative_path

    def cleaning(self, raw_relative_path: str) -> str:
        dataframe = inmemory_datalake_service.download(
            bucket_name=datalake_settings.bucket_name,
            relative_path=raw_relative_path
        )

        cleaned_dataframe = self.dataset.get_processor("inmemory").clean(dataframe)

        relative_path = generate_relative_path(DatalakeEnv.CLEANED, self.ingestion_time, self.dataset.name.lower())
        inmemory_datalake_service.upload(
            df=cleaned_dataframe,
            bucket_name=datalake_settings.bucket_name,
            relative_path=relative_path
        )

        return relative_path

    def enriching(self, cleaned_relative_path: str) -> str:
        dataframe = inmemory_datalake_service.download(
            bucket_name=datalake_settings.bucket_name,
            relative_path=cleaned_relative_path
        )
        enriched_dataframe = self.dataset.get_processor("inmemory").enrich(dataframe)

        relative_path = generate_relative_path(DatalakeEnv.ENRICHED, self.ingestion_time, self.dataset.name.lower())
        inmemory_datalake_service.upload(
            df=enriched_dataframe,
            bucket_name=datalake_settings.bucket_name,
            relative_path=relative_path
        )

        return relative_path

    def download_enriched_data(self, relative_path: str) -> pd.DataFrame:
        return inmemory_datalake_service.download(
            bucket_name=datalake_settings.bucket_name,
            relative_path=relative_path
        )

    def populate_database(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating operational database with enriched data")
        database_service.populate(self.dataset, enriched_dataframe)

    def populate_datawarehouse(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating data warehouse with enriched data")
        datawarehouse_service.truncate_and_populate(self.dataset.get_destination("datawarehouse"), enriched_dataframe)

    def show_dataframe(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Displaying enriched data")
        show(enriched_dataframe)
        log_line()

    def analyze_primary(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Analyzing enriched data via memory")
        results = self.dataset.get_processor("inmemory").analyze(enriched_dataframe)
        show_map_of_dataframe(results)

    def analyzing_via_datawarehouse(self):
        result = datawarehouse_service.analyze(self.dataset.get_destination("datawarehouse"))
        logger.info("Analyzing enriched data via data warehouse")
        show_map_of_dataframe(result)
