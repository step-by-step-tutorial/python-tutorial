from abc import ABC, abstractmethod

from sklearn.pipeline import Pipeline


class PipelineBuilder(ABC):
    @abstractmethod
    def build(self) -> Pipeline:
        raise NotImplementedError
