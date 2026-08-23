from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Generic, TypeVar


DataFrameType = TypeVar("DataFrameType")


class DatasetAnalyzer(ABC, Generic[DataFrameType]):
    @abstractmethod
    def analyze(self, dataframe: DataFrameType) -> Mapping[str, DataFrameType]:
        raise NotImplementedError
