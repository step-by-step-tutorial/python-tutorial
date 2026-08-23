import logging

import pandas as pd

from data_platform.audit.audit_service import AuditService
from data_platform.config.data_lake_environment import DataLakeEnvironment
from data_platform.config.keys import Key
from data_platform.model import DataLakeEndpoint, Dataset
from data_platform.persistence.data_lake_repository import DataLakeRepository
from data_platform.pipeline.batch_pipeline import BatchPipeline
from data_platform.presentation.dataframe_display import show, show_map_of_dataframe
from data_platform.registry.ingestor_registry import ingestor_registry
from data_platform.service.dataframe_analysis_service import DataFrameAnalyzer
from data_platform.util.log_utils import log_line
from data_platform.util.path_utils import generate_relative_path

logger = logging.getLogger(__name__)


class OnlineShoppingInmemoryPipeline(BatchPipeline):
    def __init__(self, dataset: Dataset) -> None:
        super().__init__(dataset, audit_service=AuditService(dataset.audit))
        self.pipeline_name = "online_shopping_inmemory_pipeline"
        self._data_lake_repository = DataLakeRepository(
            self.dataset.get_endpoint(Key.ONLINE_SHOPPING_DATA_LAKE, DataLakeEndpoint)
        )
        self._raw_data_ingestor = ingestor_registry.get_item(Key.ONLINE_SHOPPING_REST_API)
        self._analyzers = (
            DataFrameAnalyzer(
                self.download_enriched_data,
                self.dataset.get_analyzer("inmemory"),
                show_map_of_dataframe,
            ),
        )

    def ingest_raw_data(self) -> pd.DataFrame:
        return self._raw_data_ingestor.ingest()

    def store_raw_data(self, raw_data: pd.DataFrame) -> str:
        relative_path = self._path_for(DataLakeEnvironment.RAW)
        self._data_lake_repository.save(df=raw_data, relative_path=relative_path)
        return relative_path

    def clean(self, raw_relative_path: str) -> pd.DataFrame:
        return self.dataset.get_transformer("inmemory").clean(self._data_lake_repository.find(raw_relative_path))

    def store_cleaned_data(self, cleaned_data: pd.DataFrame) -> str:
        relative_path = self._path_for(DataLakeEnvironment.CLEANED)
        self._data_lake_repository.save(df=cleaned_data, relative_path=relative_path)
        return relative_path

    def enrich(self, cleaned_relative_path: str) -> pd.DataFrame:
        return self.dataset.get_transformer("inmemory").enrich(self._data_lake_repository.find(cleaned_relative_path))

    def store_enriched_data(self, enriched_data: pd.DataFrame) -> str:
        relative_path = self._path_for(DataLakeEnvironment.ENRICHED)
        self._data_lake_repository.save(df=enriched_data, relative_path=relative_path)
        return relative_path

    def download_enriched_data(self, enriched_data_path: str) -> pd.DataFrame:
        return self._data_lake_repository.find(enriched_data_path)

    def show_dataframe(self, enriched_data_path: str) -> None:
        logger.info("Displaying online-shopping enriched data")
        show(self.download_enriched_data(enriched_data_path))
        log_line()

    def _path_for(self, environment: DataLakeEnvironment) -> str:
        return generate_relative_path(environment, self.ingestion_time, self.dataset.name)
