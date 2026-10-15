from abc import ABC, abstractmethod

from ml_platform.model.artifact_model import ArtifactModel
from ml_platform.model.training_result_model import TrainingResultModel


class Visualizer(ABC):
    @abstractmethod
    def render(self, result: TrainingResultModel) -> tuple[ArtifactModel, ...]:
        ...
