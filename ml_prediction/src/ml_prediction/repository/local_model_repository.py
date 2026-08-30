import json
import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib

from ml_prediction.evaluation.model_evaluator import ClassificationMetrics, RegressionMetrics
from ml_prediction.model.model_metadata import ModelMetadata

logger = logging.getLogger(__name__)


class LocalModelRepository:
    def save(self, model: Any, path: Path, metadata: ModelMetadata | None = None) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, path)
        if metadata is not None:
            self.save_metadata(metadata, path)
        logger.info("Saved model: path=%s", path)
        return path

    def load(self, path: Path) -> Any:
        logger.info("Loading model: path=%s", path)
        return joblib.load(path)

    def save_metadata(self, metadata: ModelMetadata, model_path: Path) -> Path:
        metadata_path = self.metadata_path(model_path)
        with metadata_path.open("w", encoding="utf-8") as metadata_file:
            json.dump(asdict(metadata), metadata_file, default=self._json_default, indent=2)
        logger.info("Saved model metadata: path=%s", metadata_path)
        return metadata_path

    def load_metadata(self, model_path: Path) -> ModelMetadata:
        with self.metadata_path(model_path).open(encoding="utf-8") as metadata_file:
            data = json.load(metadata_file)
        data["training_timestamp"] = datetime.fromisoformat(data["training_timestamp"])
        data["numeric_features"] = tuple(data["numeric_features"])
        data["boolean_features"] = tuple(data["boolean_features"])
        data["categorical_features"] = tuple(data["categorical_features"])
        metric_type = data.get("task_type", "regression")
        metrics_model = ClassificationMetrics if metric_type == "classification" else RegressionMetrics
        data["validation_metrics"] = metrics_model(**data["validation_metrics"])
        data["final_test_metrics"] = metrics_model(**data["final_test_metrics"])
        return ModelMetadata(
            **data,
        )

    @staticmethod
    def metadata_path(model_path: Path) -> Path:
        return model_path.with_suffix(".metadata.json")

    @staticmethod
    def _json_default(value: Any) -> str:
        if hasattr(value, "isoformat"):
            return value.isoformat()
        raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")
