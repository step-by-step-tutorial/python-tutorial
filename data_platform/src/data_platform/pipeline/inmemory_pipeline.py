import logging

import pandas as pd

from data_platform.audit.audit_service import AuditService
from data_platform.config.data_lake_environment import DataLakeEnvironment
from data_platform.keys import Key
from data_platform.model import DataLakeEndpoint, DatabaseEndpoint, Dataset, DataWarehouseEndpoint, FileEndpoint
from data_platform.persistence.data_lake_repository import DataLakeRepository
from data_platform.persistence.inmemory_data_warehouse_repository import InmemoryDataWarehouseRepository
from data_platform.persistence.inmemory_database_repository import InmemoryDatabaseRepository
from data_platform.persistence.repository_data_populator import RepositoryDataPopulator
from data_platform.pipeline.batch_pipeline import BatchPipeline
from data_platform.service.dataframe_analysis_service import DataFrameAnalyzer
from data_platform.service.data_warehouse_analysis_service import DataWarehouseAnalyzer
from data_platform.presentation.dataframe_display import show
from data_platform.presentation.dataframe_display import show_map_of_dataframe
from data_platform.registry.ingestor_registry import ingestor_registry
from data_platform.util.log_utils import log_line
from data_platform.util.path_utils import generate_relative_path

logger = logging.getLogger(__name__)


class InmemoryPipeline(BatchPipeline):

    def __init__(self, ds: Dataset) -> None:
        super().__init__(ds, audit_service=AuditService(ds.audit))
        self.pipeline_name = "inmemory_pipeline"
        self._database_repository = InmemoryDatabaseRepository(
            self.dataset.get_endpoint(Key(f"{self.dataset.name.lower()}.database"), DatabaseEndpoint)
        )
        self._data_lake_repository = DataLakeRepository(
            self.dataset.get_endpoint(Key(f"{self.dataset.name.lower()}.datalake"), DataLakeEndpoint)
        )
        self._data_warehouse_repository = InmemoryDataWarehouseRepository(
            self.dataset.get_endpoint(Key(f"{self.dataset.name.lower()}.datawarehouse"), DataWarehouseEndpoint))
        self._raw_data_ingestor = ingestor_registry.get_item(
            self.dataset.get_endpoint(Key(f"{self.dataset.name.lower()}.file.csv"), FileEndpoint).name
        )
        self._populators = (
            RepositoryDataPopulator(self.download_enriched_data, self._database_repository.replace),
            RepositoryDataPopulator(self.download_enriched_data, self._data_warehouse_repository.replace),
        )
        self._analyzers = (
            DataFrameAnalyzer(self.download_enriched_data, self.dataset.get_analyzer("inmemory"), show_map_of_dataframe),
            DataWarehouseAnalyzer(
                self._data_warehouse_repository,
                self.dataset.get_analyzer("datawarehouse"),
                show_map_of_dataframe,
            ),
        )

    def ingest_raw_data(self) -> pd.DataFrame:
        return self._raw_data_ingestor.ingest()

    def store_raw_data(self, raw_data: pd.DataFrame) -> str:
        relative_path = generate_relative_path(DataLakeEnvironment.RAW, self.ingestion_time, self.dataset.name.lower())
        self._data_lake_repository.save(df=raw_data, relative_path=relative_path)
        return relative_path

    def clean(self, raw_relative_path: str) -> pd.DataFrame:
        raw_dataframe = self._data_lake_repository.find(raw_relative_path)
        return self.dataset.get_transformer("inmemory").clean(raw_dataframe)

    def store_cleaned_data(self, cleaned_data: pd.DataFrame) -> str:
        relative_path = generate_relative_path(DataLakeEnvironment.CLEANED, self.ingestion_time,
                                               self.dataset.name.lower())
        self._data_lake_repository.save(df=cleaned_data, relative_path=relative_path)
        return relative_path

    def enrich(self, cleaned_relative_path: str) -> pd.DataFrame:
        cleaned_dataframe = self._data_lake_repository.find(cleaned_relative_path)
        return self.dataset.get_transformer("inmemory").enrich(cleaned_dataframe)

    def store_enriched_data(self, enriched_data: pd.DataFrame) -> str:
        relative_path = generate_relative_path(DataLakeEnvironment.ENRICHED, self.ingestion_time,
                                               self.dataset.name.lower())
        self._data_lake_repository.save(df=enriched_data, relative_path=relative_path)
        return relative_path

    def download_enriched_data(self, enriched_data_path: str) -> pd.DataFrame:
        return self._data_lake_repository.find(enriched_data_path)

    def show_dataframe(self, enriched_data_path: str):
        enriched_dataframe = self.download_enriched_data(enriched_data_path)
        logger.info("Displaying enriched data")
        show(enriched_dataframe)
        log_line()
