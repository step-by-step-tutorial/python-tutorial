import logging

from ml_prediction.training.training_models import TrainingOutput
from ml_prediction.presentation.presenter import Presenter

logger = logging.getLogger(__name__)


class TrainingPresenter(Presenter):
    def present(self, result: TrainingOutput) -> None:
        logger.info(
            "Training result: model=%s",
            result.model_path,
        )
        logger.info("Training report: path=%s", result.report_path)
        logger.info(
            "Baseline validation metrics: mae=%.2f rmse=%.2f r2=%.4f",
            result.baseline_validation_metrics.mean_absolute_error,
            result.baseline_validation_metrics.root_mean_squared_error,
            result.baseline_validation_metrics.r2_score,
        )
        logger.info(
            "Validation metrics: mae=%.2f rmse=%.2f r2=%.4f",
            result.validation_metrics.mean_absolute_error,
            result.validation_metrics.root_mean_squared_error,
            result.validation_metrics.r2_score,
        )
        logger.info(
            "Final test metrics: mae=%.2f rmse=%.2f r2=%.4f",
            result.test_metrics.mean_absolute_error,
            result.test_metrics.root_mean_squared_error,
            result.test_metrics.r2_score,
        )
