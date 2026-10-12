from abc import ABC, abstractmethod

from ml_prediction.model.artifact_model import ArtifactModel
from ml_prediction.model.training_result_model import TrainingResultModel


class Visualizer(ABC):
    @abstractmethod
    def render(self, result: TrainingResultModel) -> tuple[ArtifactModel, ...]:
        ...
