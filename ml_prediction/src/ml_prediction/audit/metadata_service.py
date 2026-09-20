import json
from datetime import datetime
from pathlib import Path

from ml_prediction.audit.data.metadata import Metadata
from ml_prediction.audit.data_service import DataService
from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.utils.metrics_utils import create_metrics


class MetadataService(DataService):
    def read(self, path: Path) -> Metadata:
        path = path.with_suffix(".metadata.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        task_type = data.get("task_type", "regression")
        data["training_timestamp"] = datetime.fromisoformat(data["training_timestamp"])
        data["numeric_features"] = tuple(data["numeric_features"])
        data["boolean_features"] = tuple(data["boolean_features"])
        data["categorical_features"] = tuple(data["categorical_features"])
        metric_type = ClassificationMetrics if task_type == "classification" else RegressionMetrics
        data["validation_metrics"] = create_metrics(data["validation_metrics"], metric_type)
        data["final_test_metrics"] = create_metrics(data["final_test_metrics"], metric_type)
        return Metadata(**data)

    def write(self, data: Metadata, path: Path):
        path = path.with_suffix(".metadata.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data.to_dict(), indent=2), encoding="utf-8")
