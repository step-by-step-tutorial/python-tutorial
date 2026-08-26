import logging

import pandas as pd

from data_platform.model.dataset_ingestor import DatasetIngestor
from data_platform.model.endpoints import FileEndpoint
from data_platform.util.csv_utils import csv_to_dataframe

logger = logging.getLogger(__name__)


class CsvFileIngestor(DatasetIngestor):
    def __init__(self, endpoint: FileEndpoint) -> None:
        self._endpoint = endpoint
        self.name = "csv"

    def ingest(self) -> pd.DataFrame:
        logger.info("Ingesting CSV file from %s", self._endpoint.file_path)
        data = csv_to_dataframe(self._endpoint.file_path)
        return data
