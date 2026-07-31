from pathlib import Path

from pandas import DataFrame

import pandas as pd
from pandas.errors import EmptyDataError


def read_csv_file(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    try:
        df: DataFrame = pd.read_csv(path)
    except EmptyDataError as error:
        raise ValueError(f"CSV file is empty: {path}") from error
    except pd.errors.ParserError as error:
        raise ValueError(f"CSV file is invalid: {path}") from error

    if df.empty:
        raise ValueError(f"CSV file contains no data rows: {path}")

    return df


def must_has_columns(df: DataFrame, columns: set[str]) -> None:
    if df is None or columns is None:
        raise ValueError("required columns or dataframe is None")

    missing_columns = columns.difference(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")
