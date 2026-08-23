from abc import ABC, abstractmethod
from typing import Generic, TypeVar


DataFrameType = TypeVar("DataFrameType")


class DatasetTransformer(ABC, Generic[DataFrameType]):
    @abstractmethod
    def clean(self, dataframe: DataFrameType) -> DataFrameType:
        raise NotImplementedError

    @abstractmethod
    def enrich(self, dataframe: DataFrameType) -> DataFrameType:
        raise NotImplementedError
