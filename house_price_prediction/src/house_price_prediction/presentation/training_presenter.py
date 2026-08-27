import logging

from house_price_prediction.training.training_models import TrainingOutput

logger = logging.getLogger(__name__)


class TrainingPresenter:
    def present(self, result: TrainingOutput) -> None:
        logger.info(
            "Training result: model=%s baseline_mae=%.2f validation_mae=%.2f test_mae=%.2f test_r2=%.4f",
            result.model_path,
            result.baseline_metrics.mean_absolute_error,
            result.validation_metrics.mean_absolute_error,
            result.model_metrics.mean_absolute_error,
            result.model_metrics.r2_score,
        )
