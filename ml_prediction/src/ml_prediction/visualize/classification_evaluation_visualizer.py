from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from sklearn.metrics import ConfusionMatrixDisplay

from ml_prediction.audit.data.artifact_category import ArtifactCategory
from ml_prediction.audit.data.artifact_dto import ArtifactDto
from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto
from ml_prediction.config.settings import get_settings
from ml_prediction.visualize.visualizer import Visualizer


class ClassificationEvaluationVisualizer(Visualizer):

    def __init__(self, dataset_name: str) -> None:
        self._settings = get_settings(dataset_name)

    def render(self, dto: TrainingAuditDto) -> tuple[ArtifactDto, ...]:
        if dto.evaluation is None or dto.experiment is None:
            return ()

        path = self.save_confusion_matrix(dto.evaluation.y_true, dto.evaluation.y_pred, dto.experiment.run_id)
        return (ArtifactDto(path, ArtifactCategory.PLOTS),)

    def save_confusion_matrix(self, y_true, y_pred, run_id: str) -> Path:
        path = self._settings.artifact_path(run_id, self._settings.confusion_matrix_filename)
        display = ConfusionMatrixDisplay.from_predictions(y_true, y_pred)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            display.figure_.tight_layout()
            display.figure_.savefig(path)
        finally:
            plt.close(display.figure_)
        return path
