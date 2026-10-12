import json
import logging
from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline

from ml_prediction.model.metadata_model import MetadataModel

logger = logging.getLogger(__name__)


class ModelRepository:

    @staticmethod
    def metadata_path(model_path: Path) -> Path:
        return model_path.with_suffix(".metadata.json")

    def save(self, path: Path, pipeline: Pipeline, metadata: MetadataModel) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, path)
        self.metadata_path(path).write_text(json.dumps(metadata.to_dict(), indent=2), encoding="utf-8")
        logger.info("Saved model: path=%s", path)

    def load(self, path: Path) -> Pipeline:
        logger.info("Loading model: path=%s", path)
        return joblib.load(path)

    def load_metadata(self, path: Path) -> MetadataModel:
        return MetadataModel.from_dict(json.loads(self.metadata_path(path).read_text(encoding="utf-8")))
