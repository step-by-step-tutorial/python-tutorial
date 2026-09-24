import logging

from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto
from ml_prediction.visualize.visualizer import Visualizer

logger = logging.getLogger(__name__)


class CliVisualizer(Visualizer):
    def render(self, dto: TrainingAuditDto) -> None:
        experiment = dto.experiment
        if experiment is None:
            return
        logger.info(f"ExperimentDto completed: {experiment.to_string()}")
        logger.info("Validation metrics: %s", experiment.validation_metrics.to_string())
        logger.info("Final test metrics: %s", experiment.test_metrics.to_string())
        logger.info(f"Saved model: path={experiment.model_path}")
        logger.info(f"ExperimentDto history: path={experiment.audit_path}")
