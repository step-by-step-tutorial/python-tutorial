from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Generic, TypeVar

AnalysisSource = TypeVar("AnalysisSource")


class DatasetAnalyzer(ABC, Generic[AnalysisSource]):
    @abstractmethod
    def analyze(self, data: AnalysisSource) -> Mapping[str, AnalysisSource]:
        raise NotImplementedError
