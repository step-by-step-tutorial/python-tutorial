from typing import Any

from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto
from ml_prediction.visualize.visualizer import Visualizer


class JsonVisualizer(Visualizer):

    def render(self, dto: TrainingAuditDto) -> dict[str, Any]:
        if dto.experiment is None:
            return {}
        return {
            "run_id": dto.experiment.run_id,
            "dataset_name": dto.experiment.dataset_name,
            "model_type": dto.experiment.model_type,
            "validation_metrics": dto.experiment.validation_metrics.__dict__,
            "test_metrics": dto.experiment.test_metrics.__dict__,
            "model_path": str(dto.experiment.model_path),
            "audit_path": str(dto.experiment.audit_path) if dto.experiment.audit_path else None,
        }
