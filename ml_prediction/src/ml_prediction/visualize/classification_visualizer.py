from sklearn.metrics import ConfusionMatrixDisplay

from ml_prediction.config.artifact_category import ArtifactCategory
from ml_prediction.model.artifact_model import ArtifactModel
from ml_prediction.model.settings_model import SettingsModel
from ml_prediction.model.training_result_model import TrainingResultModel
from ml_prediction.util.visualization_utils import save_figure
from ml_prediction.visualize.visualizer import Visualizer


class ClassificationVisualizer(Visualizer):
    def __init__(self, settings: SettingsModel) -> None:
        self._settings = settings

    def render(self, result: TrainingResultModel) -> tuple[ArtifactModel, ...]:
        evaluation = result.test_evaluation
        display = ConfusionMatrixDisplay.from_predictions(evaluation.actual, evaluation.predicted)
        path = save_figure(display.figure_, self._settings.artifact_path(result.experiment.run_id,
                                                                          "confusion_matrix.png"))
        return (ArtifactModel(path, ArtifactCategory.PLOTS),)
