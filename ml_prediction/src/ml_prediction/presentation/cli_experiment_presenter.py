import logging
from ml_prediction.audit.data.training_audit_data import TrainingAuditData

from ml_prediction.audit.data.experiment_data import ExperimentData
from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.presentation.presenter import Presenter

logger = logging.getLogger(__name__)


class CliExperimentPresenter(Presenter):
    def present(self, data: TrainingAuditData) -> None:
        output: ExperimentData | None = data.experiment
        if output is None:
            return
        logger.info(
            "ExperimentData completed: run_id=%s dataset=%s model_type=%s",
            output.run_id,
            output.dataset_name,
            output.model_type,
        )
        self._log_metrics("Validation", output.validation_metrics)
        self._log_metrics("Final test", output.test_metrics)
        logger.info("Saved model: path=%s", output.model_path)
        logger.info("ExperimentData history: path=%s", output.audit_path)

    @staticmethod
    def _log_metrics(label: str, metrics: RegressionMetrics | ClassificationMetrics) -> None:
        if isinstance(metrics, RegressionMetrics):
            logger.info(
                "%s metrics: mae=%.2f rmse=%.2f r2=%.4f",
                label, metrics.mean_absolute_error, metrics.root_mean_squared_error, metrics.r2_score,
            )
        else:
            logger.info(
                "%s metrics: accuracy=%.4f precision=%.4f recall=%.4f f1=%.4f",
                label, metrics.accuracy, metrics.precision, metrics.recall, metrics.f1_score,
            )
