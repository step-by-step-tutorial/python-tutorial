from typing import Any

from ml_prediction.audit.data.training_audit_data import TrainingAuditData
from ml_prediction.presentation.presenter import Presenter


class WebExperimentPresenter(Presenter):

    def present(self, data: TrainingAuditData) -> dict[str, Any]:
        if data.experiment is None:
            return {}
        return {
            "run_id": data.experiment.run_id,
            "dataset_name": data.experiment.dataset_name,
            "model_type": data.experiment.model_type,
            "validation_metrics": data.experiment.validation_metrics.__dict__,
            "test_metrics": data.experiment.test_metrics.__dict__,
            "model_path": str(data.experiment.model_path),
            "audit_path": str(data.experiment.audit_path) if data.experiment.audit_path else None,
        }
