import logging

import pandas as pd

from data_platform.model.endpoints import DataLakeEndpoint
from data_platform.repository.inmemory_datalake_repository import DataLakeRepository

logger = logging.getLogger(__name__)


class DataLakeIngestor:
    def __init__(self, endpoint: DataLakeEndpoint) -> None:
        self._repository = DataLakeRepository(endpoint)

    def ingest(self, relative_path: str, file_extension: str = "parquet") -> pd.DataFrame:
        logger.info("Ingesting %s data from data lake path %s", file_extension, relative_path)
        return self._repository.read(relative_path, file_extension)
