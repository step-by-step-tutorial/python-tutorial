from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd


class CleanerChain:
    def __init__(self, cleaners: tuple[Any, ...]) -> None:
        self.cleaners = cleaners

    def clean(self, dataframe: Any) -> Any:
        for cleaner in self.cleaners:
            dataframe = cleaner.clean(dataframe)
        return dataframe


class DropDuplicatesCleaner:
    def __init__(self, subset: str | Sequence[str] | None = None) -> None:
        self.subset = subset

    def clean(self, dataframe: Any) -> Any:
        return dataframe.drop_duplicates(subset=self.subset)


class NumericColumnCleaner:
    def __init__(self, column: str, default_value: float | int | None = None) -> None:
        self.column, self.default_value = column, default_value

    def clean(self, dataframe: Any) -> Any:
        converted = pd.to_numeric(dataframe[self.column].astype("string").str.replace(",", "", regex=False).str.strip(), errors="coerce")
        dataframe[self.column] = converted if self.default_value is None else converted.fillna(self.default_value)
        return dataframe


class CastColumnCleaner:
    def __init__(self, column: str, dtype: str) -> None:
        self.column, self.dtype = column, dtype

    def clean(self, dataframe: Any) -> Any:
        dataframe[self.column] = dataframe[self.column].astype(self.dtype)
        return dataframe


class ToDatetimeCleaner:
    def __init__(self, column: str) -> None:
        self.column = column

    def clean(self, dataframe: Any) -> Any:
        dataframe[self.column] = pd.to_datetime(dataframe[self.column], errors="coerce")
        return dataframe


class BooleanColumnCleaner:
    def __init__(self, column: str, default_value: bool = False) -> None:
        self.column, self.default_value = column, default_value

    def clean(self, dataframe: Any) -> Any:
        def convert(value: object) -> bool:
            if pd.isna(value):
                return self.default_value
            if isinstance(value, bool):
                return value
            if isinstance(value, (int, float)):
                return bool(value)
            return str(value).strip().lower() in {"true", "1", "yes", "y"}
        dataframe[self.column] = dataframe[self.column].map(convert).astype(bool)
        return dataframe


class RenameColumnsCleaner:
    def __init__(self, columns: Mapping[str, str]) -> None:
        self.columns = columns

    def clean(self, dataframe: Any) -> Any:
        return dataframe.rename(columns=self.columns)


class StripColumnCleaner:
    def __init__(self, column: str) -> None:
        self.column = column

    def clean(self, dataframe: Any) -> Any:
        dataframe[self.column] = dataframe[self.column].astype("string").str.strip()
        return dataframe


class FillMissingByGroupAverageCleaner:
    def __init__(self, group_column: str, column: str) -> None:
        self.group_column, self.column = group_column, column

    def clean(self, dataframe: Any) -> Any:
        average = dataframe.groupby(self.group_column)[self.column].transform("mean")
        dataframe[self.column] = dataframe[self.column].fillna(average)
        return dataframe


class FillMissingByColumnAverageCleaner:
    def __init__(self, column: str) -> None:
        self.column = column

    def clean(self, dataframe: Any) -> Any:
        average = dataframe[self.column].mean()
        if pd.isna(average):
            raise ValueError(f"No valid values are available for '{self.column}'.")
        dataframe[self.column] = dataframe[self.column].fillna(average)
        return dataframe
