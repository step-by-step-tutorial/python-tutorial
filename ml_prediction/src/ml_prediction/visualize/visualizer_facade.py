from ml_prediction.audit.data.artifact_dto import ArtifactDto
from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType
from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto
from ml_prediction.visualize.classification_evaluation_visualizer import ClassificationEvaluationVisualizer
from ml_prediction.visualize.cli_visualizer import CliVisualizer
from ml_prediction.visualize.evaluation_visualizer import EvaluationVisualizer
from ml_prediction.visualize.experiment_visualizer import ExperimentVisualizer
from ml_prediction.visualize.model_interpretability_visualizer import ModelInterpretabilityVisualizer
from ml_prediction.visualize.visualizer import Visualizer


class VisualizationFacade:
    def __init__(self, dataset_name: str) -> None:
        self._visualizers: dict[ExperimentTaskType, tuple[Visualizer, ...]] = {
            ExperimentTaskType.REGRESSION: (
                EvaluationVisualizer(dataset_name),
                ModelInterpretabilityVisualizer(dataset_name),
                ExperimentVisualizer(dataset_name),
                CliVisualizer(),
            ),
            ExperimentTaskType.CLASSIFICATION: (
                ClassificationEvaluationVisualizer(dataset_name),
                CliVisualizer(),
            ),
            ExperimentTaskType.UNKNOWN: (
                CliVisualizer(),
            ),
        }

    def visualize(self, dto: TrainingAuditDto) -> tuple[ArtifactDto, ...]:
        if dto.experiment is None:
            return ()

        artifacts: list[ArtifactDto] = []
        for visualizer in self._visualizers[dto.experiment.task_type]:
            artifacts.extend(visualizer.render(dto))
        return tuple(artifacts)
