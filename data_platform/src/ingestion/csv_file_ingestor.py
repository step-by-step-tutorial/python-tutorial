from __future__ import annotations

from pathlib import Path

import pandas as pd

from util.csv_utils import csv_to_dataframe


class CsvFileIngestor:
    def __init__(self, file_path: str | Path) -> None:
        self.file_path = file_path

    def ingest(self) -> pd.DataFrame:
        return csv_to_dataframe(Path(self.file_path))
