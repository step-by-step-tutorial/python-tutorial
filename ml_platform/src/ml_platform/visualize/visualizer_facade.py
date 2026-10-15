from ml_platform.config.task_type import TaskType
from ml_platform.model.artifact_model import ArtifactModel
from ml_platform.model.settings_model import SettingsModel
from ml_platform.model.training_result_model import TrainingResultModel
from ml_platform.visualize.classification_visualizer import ClassificationVisualizer
from ml_platform.visualize.experiment_visualizer import ExperimentVisualizer
from ml_platform.visualize.regression_visualizer import RegressionVisualizer
from ml_platform.visualize.visualizer import Visualizer


class VisualizerFacade:
    def __init__(self, settings: SettingsModel) -> None:
        visualizers: dict[TaskType, tuple[Visualizer, ...]] = {
            TaskType.REGRESSION: (RegressionVisualizer(settings), ExperimentVisualizer(settings)),
            TaskType.CLASSIFICATION: (ClassificationVisualizer(settings),),
        }
        self._visualizers = visualizers[settings.task_type]

    def render(self, result: TrainingResultModel) -> tuple[ArtifactModel, ...]:
        return tuple(artifact for visualizer in self._visualizers for artifact in visualizer.render(result))
