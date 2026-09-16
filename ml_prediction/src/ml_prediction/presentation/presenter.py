from abc import ABC, abstractmethod
from typing import Any

from ml_prediction.presentation.experiment_data import ExperimentData


class Presenter(ABC):
    @abstractmethod
    def present(self, output: ExperimentData) -> Any:
        raise NotImplementedError
