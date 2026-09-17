from typing import Any

from ml_prediction.audit.data.experiment_audit_data import ExperimentAuditData
from ml_prediction.presentation.presenter import Presenter


class WebExperimentPresenter(Presenter):
    """Produces a JSON-ready representation for a web or API adapter."""

    def present(self, data: ExperimentAuditData) -> dict[str, Any]:
        if data.experiment is None:
            return {}
        return {
            "experiment_id": data.experiment.experiment_id,
            "dataset_name": data.experiment.dataset_name,
            "model_type": data.experiment.model_type,
            "validation_metrics": data.experiment.validation_metrics.__dict__,
            "test_metrics": data.experiment.test_metrics.__dict__,
            "model_path": str(data.experiment.model_path),
            "audit_path": str(data.experiment.audit_path) if data.experiment.audit_path else None,
        }
