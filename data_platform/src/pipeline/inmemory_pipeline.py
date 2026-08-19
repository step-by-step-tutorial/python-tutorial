import logging

import pandas as pd

from audit.audit_service import AuditService
from dataset.definition import DataLakeEndpoint, DatabaseEndpoint, Dataset, DataWarehouseEndpoint
from ingestion.registry import get_ingestor
from persistence.database_repository import DatabaseRepository
from persistence.datalake_repository import DataLakeRepository
from persistence.datawarehouse_repository import DataWarehouseRepository
from pipeline.batch_pipeline import BatchPipeline
from presentation.dataframe_display import show
from presentation.dataframe_display import show_map_of_dataframe
from util.log_utils import log_line
from util.path_utils import DatalakeEnv, generate_relative_path

logger = logging.getLogger(__name__)


class InmemoryPipeline(BatchPipeline):

    def __init__(self, ds: Dataset) -> None:
        super().__init__(ds, audit_service=AuditService(ds.audit))
        self.pipeline_name = "inmemory_pipeline"
        self.database_repository = DatabaseRepository(self.dataset.get_endpoint("sale.database", DatabaseEndpoint))
        self.datalake_repository = DataLakeRepository(self.dataset.get_endpoint("sale.datalake", DataLakeEndpoint))
        self.datawarehouse_repository = DataWarehouseRepository(self.dataset.get_endpoint("sale.datawarehouse", DataWarehouseEndpoint))
        self.raw_data_ingestor = get_ingestor("sale.file.csv")

    def ingest_raw_data(self) -> pd.DataFrame:
        return self.raw_data_ingestor.ingest()

    def store_raw_data(self, raw_data: pd.DataFrame) -> str:
        relative_path = generate_relative_path(DatalakeEnv.RAW, self.ingestion_time, self.dataset.name.lower())
        self.datalake_repository.upload(df=raw_data, relative_path=relative_path)
        return relative_path

    def cleaning(self, raw_relative_path: str) -> pd.DataFrame:
        raw_dataframe = self.datalake_repository.download(raw_relative_path)
        return self.dataset.get_processor("inmemory").clean(raw_dataframe)

    def store_cleaned_data(self, cleaned_data: pd.DataFrame) -> str:
        relative_path = generate_relative_path(DatalakeEnv.CLEANED, self.ingestion_time, self.dataset.name.lower())
        self.datalake_repository.upload(df=cleaned_data, relative_path=relative_path)
        return relative_path

    def enriching(self, cleaned_relative_path: str) -> pd.DataFrame:
        cleaned_dataframe = self.datalake_repository.download(cleaned_relative_path)
        return self.dataset.get_processor("inmemory").enrich(cleaned_dataframe)

    def store_enriched_data(self, enriched_data: pd.DataFrame) -> str:
        relative_path = generate_relative_path(DatalakeEnv.ENRICHED, self.ingestion_time, self.dataset.name.lower())
        self.datalake_repository.upload(df=enriched_data, relative_path=relative_path)
        return relative_path

    def download_enriched_data(self, relative_path: str) -> pd.DataFrame:
        return self.datalake_repository.download(relative_path)

    def populate_database(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating operational database with enriched data")
        self.database_repository.truncate_and_populate_from_memory(enriched_dataframe)

    def populate_datawarehouse(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating data warehouse with enriched data")
        self.datawarehouse_repository.truncate_and_populate_from_memory(enriched_dataframe)

    def analyze_via_dataframe(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Analyzing enriched data via memory")
        results = self.dataset.get_processor("inmemory").analyze(enriched_dataframe)
        show_map_of_dataframe(results)

    def analyzing_via_datawarehouse(self):
        query_names = [name for name in self.datawarehouse_repository.datawarehouse.query_sql_files.keys() if name != "select_all"]
        result = self.datawarehouse_repository.analyze(query_names)
        logger.info("Analyzing enriched data via data warehouse")
        show_map_of_dataframe(result)

    def show_dataframe(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Displaying enriched data")
        show(enriched_dataframe)
        log_line()
