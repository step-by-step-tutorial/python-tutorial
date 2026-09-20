from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.regression_metrics import RegressionMetrics

CURRENT_SCHEMA_VERSION = "1"
CURRENT_MODEL_VERSION = "1"


@dataclass(frozen=True)
class Metadata(AuditData):
    model_type: str
    model_parameters: dict[str, Any]
    target_column: str
    numeric_features: tuple[str, ...]
    boolean_features: tuple[str, ...]
    categorical_features: tuple[str, ...]
    training_timestamp: datetime
    validation_metrics: RegressionMetrics | ClassificationMetrics
    final_test_metrics: RegressionMetrics | ClassificationMetrics
    schema_version: str
    model_version: str
    dataset_name: str = "house"
    task_type: str = "regression"
    prediction_column: str = "predicted_total_price"
    run_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["training_timestamp"] = self.training_timestamp.isoformat()
        value["validation_metrics"] = {
            key: float(metric) for key, metric in asdict(self.validation_metrics).items()
        }
        value["final_test_metrics"] = {
            key: float(metric) for key, metric in asdict(self.final_test_metrics).items()
        }
        return value
