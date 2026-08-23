
import pandas as pd

from data_platform.model import FileEndpoint
from data_platform.util.csv_utils import csv_to_dataframe


class CsvFileIngestor:
    def __init__(self, endpoint: FileEndpoint) -> None:
        self.endpoint = endpoint

    def ingest(self) -> pd.DataFrame:
        return csv_to_dataframe(self.endpoint.file_path)
