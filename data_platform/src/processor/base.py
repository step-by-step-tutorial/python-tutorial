from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Generic, TypeVar

DataFrameType = TypeVar("DataFrameType")


class DataProcessor(ABC, Generic[DataFrameType]):

    @abstractmethod
    def clean(self, dataframe: DataFrameType) -> DataFrameType:
        raise NotImplementedError

    @abstractmethod
    def enrich(self, dataframe: DataFrameType) -> DataFrameType:
        raise NotImplementedError

    @abstractmethod
    def analyze(self, dataframe: DataFrameType) -> Mapping[str, DataFrameType]:
        raise NotImplementedError
