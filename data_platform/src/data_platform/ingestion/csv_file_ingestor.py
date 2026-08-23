import logging
import pandas as pd

from data_platform.model import FileEndpoint
from data_platform.util.csv_utils import csv_to_dataframe

logger = logging.getLogger(__name__)


class CsvFileIngestor:
    def __init__(self, endpoint: FileEndpoint) -> None:
        self._endpoint = endpoint

    def ingest(self) -> pd.DataFrame:
        logger.info("Ingesting CSV file from %s", self._endpoint.file_path)
        return csv_to_dataframe(self._endpoint.file_path)
