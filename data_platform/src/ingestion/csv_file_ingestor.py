from __future__ import annotations

from pathlib import Path

import pandas as pd

from dataset.definition import FileEndpoint
from ingestion.base import Ingestor
from util.csv_utils import csv_to_dataframe


class CsvFileIngestor(Ingestor[pd.DataFrame]):
    def __init__(self, endpoint: FileEndpoint) -> None:
        self.endpoint = endpoint

    def ingest(self) -> pd.DataFrame:
        return csv_to_dataframe(Path(self.endpoint.file_path))
