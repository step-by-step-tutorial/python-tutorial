import logging

from ml_prediction.evaluation.model_evaluator import ClassificationMetrics, RegressionMetrics
from ml_prediction.presentation.presenter import Presenter
from ml_prediction.training.training_models import TrainingOutput

logger = logging.getLogger(__name__)


class TrainingPresenter(Presenter):
    def present(self, output: TrainingOutput) -> None:
        experiment_history_path = (
            output.report_path.parent / "experiments.csv"
            if output.report_path is not None
            else None
        )
        logger.info(
            "Training experiment completed: experiment_id=%s dataset=%s model_type=%s",
            output.experiment_id,
            output.dataset_name,
            output.model_type,
        )
        self._log_metrics("Baseline validation", output.baseline_validation_metrics)
        self._log_metrics("Validation", output.validation_metrics)
        self._log_metrics("Final test", output.test_metrics)
        logger.info("Saved model: path=%s", output.model_path)
        logger.info("Experiment history: path=%s", experiment_history_path)

    @staticmethod
    def _log_metrics(label: str, metrics: RegressionMetrics | ClassificationMetrics) -> None:
        if isinstance(metrics, RegressionMetrics):
            logger.info(
                "%s metrics: mae=%.2f rmse=%.2f r2=%.4f",
                label,
                metrics.mean_absolute_error,
                metrics.root_mean_squared_error,
                metrics.r2_score,
            )
        else:
            logger.info(
                "%s metrics: accuracy=%.4f precision=%.4f recall=%.4f f1=%.4f",
                label,
                metrics.accuracy,
                metrics.precision,
                metrics.recall,
                metrics.f1_score,
            )
