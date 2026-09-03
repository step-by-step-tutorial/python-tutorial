import json
from datetime import datetime
from pathlib import Path

from ml_prediction.offline_tracking.models import ModelMetadata, metrics_from_dict


class MetadataReader:
    def load(self, model_path: Path) -> ModelMetadata:
        path = model_path.with_suffix(".metadata.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        task_type = data.get("task_type", "regression")
        data["training_timestamp"] = datetime.fromisoformat(data["training_timestamp"])
        data["numeric_features"] = tuple(data["numeric_features"])
        data["boolean_features"] = tuple(data["boolean_features"])
        data["categorical_features"] = tuple(data["categorical_features"])
        data["validation_metrics"] = metrics_from_dict(data["validation_metrics"], task_type)
        data["final_test_metrics"] = metrics_from_dict(data["final_test_metrics"], task_type)
        return ModelMetadata(**data)
