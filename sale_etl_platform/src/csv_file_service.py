import pandas as pd


class CsvFileService:
    def load_csv_file(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path)