import logging

import pandas as pd

from data_platform.audit.audit_service import AuditService
from data_platform.model import DataLakeEndpoint, DatabaseEndpoint, Dataset, DataWarehouseEndpoint
from data_platform.registry.ingestor_registry import ingestor_registry
from data_platform.keys import Key
from data_platform.persistence.database_repository import DatabaseRepository
from data_platform.persistence.data_lake_repository import DataLakeRepository
from data_platform.persistence.data_warehouse_repository import DataWarehouseRepository
from data_platform.pipeline.batch_pipeline import BatchPipeline
from data_platform.presentation.dataframe_display import show
from data_platform.presentation.dataframe_display import show_map_of_dataframe
from data_platform.util.log_utils import log_line
from data_platform.config.data_lake_environment import DataLakeEnvironment
from data_platform.util.path_utils import generate_relative_path

logger = logging.getLogger(__name__)


class InmemoryPipeline(BatchPipeline):

    def __init__(self, ds: Dataset) -> None:
        super().__init__(ds, audit_service=AuditService(ds.audit))
        self.pipeline_name = "inmemory_pipeline"
        self.database_repository = DatabaseRepository(self.dataset.get_endpoint(Key.SALE_DATABASE, DatabaseEndpoint))
        self.data_lake_repository = DataLakeRepository(self.dataset.get_endpoint(Key.SALE_DATALAKE, DataLakeEndpoint))
        self.data_warehouse_repository = DataWarehouseRepository(self.dataset.get_endpoint(Key.SALE_DATAWAREHOUSE, DataWarehouseEndpoint))
        self.raw_data_ingestor = ingestor_registry.get_item(Key.SALE_FILE_CSV)

    def ingest_raw_data(self) -> pd.DataFrame:
        return self.raw_data_ingestor.ingest()

    def store_raw_data(self, raw_data: pd.DataFrame) -> str:
        relative_path = generate_relative_path(DataLakeEnvironment.RAW, self.ingestion_time, self.dataset.name.lower())
        self.data_lake_repository.upload(df=raw_data, relative_path=relative_path)
        return relative_path

    def clean(self, raw_relative_path: str) -> pd.DataFrame:
        raw_dataframe = self.data_lake_repository.download(raw_relative_path)
        return self.dataset.get_transformer("inmemory").clean(raw_dataframe)

    def store_cleaned_data(self, cleaned_data: pd.DataFrame) -> str:
        relative_path = generate_relative_path(DataLakeEnvironment.CLEANED, self.ingestion_time, self.dataset.name.lower())
        self.data_lake_repository.upload(df=cleaned_data, relative_path=relative_path)
        return relative_path

    def enrich(self, cleaned_relative_path: str) -> pd.DataFrame:
        cleaned_dataframe = self.data_lake_repository.download(cleaned_relative_path)
        return self.dataset.get_transformer("inmemory").enrich(cleaned_dataframe)

    def store_enriched_data(self, enriched_data: pd.DataFrame) -> str:
        relative_path = generate_relative_path(DataLakeEnvironment.ENRICHED, self.ingestion_time, self.dataset.name.lower())
        self.data_lake_repository.upload(df=enriched_data, relative_path=relative_path)
        return relative_path

    def download_enriched_data(self, relative_path: str) -> pd.DataFrame:
        return self.data_lake_repository.download(relative_path)

    def populate_database(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating operational database with enriched data")
        self.database_repository.truncate_and_populate_from_memory(enriched_dataframe)

    def populate_datawarehouse(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Populating data warehouse with enriched data")
        self.data_warehouse_repository.truncate_and_populate_from_memory(enriched_dataframe)

    def analyze_dataframe(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Analyzing enriched data via memory")
        results = self.dataset.get_analyzer("inmemory").analyze(enriched_dataframe)
        show_map_of_dataframe(results)

    def analyze_data_warehouse(self):
        query_names = [name for name in self.data_warehouse_repository.datawarehouse.query_sql_files.keys() if name != "select_all"]
        result = self.data_warehouse_repository.select_by_queries(query_names)
        logger.info("Analyzing enriched data via data warehouse")
        show_map_of_dataframe(result)

    def show_dataframe(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Displaying enriched data")
        show(enriched_dataframe)
        log_line()
