from typing import Any

from ml_prediction.presentation.experiment_data import ExperimentData
from ml_prediction.presentation.presenter import Presenter


class WebExperimentPresenter(Presenter):
    """Produces a JSON-ready representation for a web or API adapter."""

    def present(self, data: ExperimentData) -> dict[str, Any]:
        if data.experiment is None:
            return {}
        return {
            "experiment_id": data.experiment.experiment_id,
            "dataset_name": data.experiment.dataset_name,
            "model_type": data.experiment.model_type,
            "validation_metrics": data.experiment.validation_metrics.__dict__,
            "test_metrics": data.experiment.test_metrics.__dict__,
            "model_path": str(data.experiment.model_path),
            "report_path": str(data.experiment.report_path) if data.experiment.report_path else None,
        }
