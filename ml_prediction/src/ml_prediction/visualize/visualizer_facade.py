from ml_prediction.audit.data.artifact_dto import ArtifactDto
from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType
from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto
from ml_prediction.visualize.cli_visualizer import CliVisualizer
from ml_prediction.visualize.visualizer import Visualizer
from ml_prediction.visualize.evaluation_visualizer import EvaluationVisualizer
from ml_prediction.visualize.experiment_visualizer import ExperimentVisualizer
from ml_prediction.visualize.model_interpretability_visualizer import ModelInterpretabilityVisualizer


class VisualizationFacade:
    def __init__(self, dataset_name: str) -> None:
        regression_visualizers = (
            EvaluationVisualizer(dataset_name),
            ModelInterpretabilityVisualizer(dataset_name),
            ExperimentVisualizer(dataset_name),
        )
        self._visualizers_by_task: dict[ExperimentTaskType, tuple[Visualizer, ...]] = {
            ExperimentTaskType.REGRESSION: regression_visualizers,
            ExperimentTaskType.CLASSIFICATION: (),
        }
        self._cli_visualizer = CliVisualizer()

    def visualize(self, dto: TrainingAuditDto) -> tuple[ArtifactDto, ...]:
        artifacts: list[ArtifactDto] = []
        if dto.experiment is None:
            self._cli_visualizer.render(dto)
            return ()
        for visualizer in self._visualizers_by_task[dto.experiment.task_type]:
            artifacts.extend(visualizer.render(dto))
        self._cli_visualizer.render(dto)
        return tuple(artifacts)
