from __future__ import annotations

import pandas as pd

from dataset.definition import FileEndpoint
from util.csv_utils import csv_to_dataframe


class CsvFileIngestor:
    def __init__(self, endpoint: FileEndpoint) -> None:
        self.endpoint = endpoint

    def ingest(self) -> pd.DataFrame:
        return csv_to_dataframe(self.endpoint.file_path)
