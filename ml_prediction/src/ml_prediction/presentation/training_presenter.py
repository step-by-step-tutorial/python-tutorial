import logging

from ml_prediction.training.training_models import TrainingOutput
from ml_prediction.presentation.presenter import Presenter

logger = logging.getLogger(__name__)


class TrainingPresenter(Presenter):
    def present(self, training_output: TrainingOutput) -> None:
        logger.info(
            "Training result: model=%s",
            training_output.model_path,
        )
        logger.info("Training report: path=%s", training_output.report_path)
        logger.info(
            "Baseline validation metrics: mae=%.2f rmse=%.2f r2=%.4f",
            training_output.baseline_validation_metrics.mean_absolute_error,
            training_output.baseline_validation_metrics.root_mean_squared_error,
            training_output.baseline_validation_metrics.r2_score,
        )
        logger.info(
            "Validation metrics: mae=%.2f rmse=%.2f r2=%.4f",
            training_output.validation_metrics.mean_absolute_error,
            training_output.validation_metrics.root_mean_squared_error,
            training_output.validation_metrics.r2_score,
        )
        logger.info(
            "Final test metrics: mae=%.2f rmse=%.2f r2=%.4f",
            training_output.test_metrics.mean_absolute_error,
            training_output.test_metrics.root_mean_squared_error,
            training_output.test_metrics.r2_score,
        )
