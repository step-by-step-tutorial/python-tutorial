import logging
from pathlib import Path
from typing import Any

import joblib

from ml_prediction.offline_tracking.metadata_reader import MetadataReader
from ml_prediction.offline_tracking.metadata_writer import MetadataWriter
from ml_prediction.offline_tracking.models import ModelMetadata

logger = logging.getLogger(__name__)


class LocalModelRepository:
    def save(self, model: Any, path: Path, metadata: ModelMetadata | None = None) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, path)
        if metadata is not None:
            self.save_metadata(metadata, path)
        logger.info(f"Saved model: path={path}")
        return path

    def load(self, path: Path) -> Any:
        logger.info(f"Loading model: path={path}")
        return joblib.load(path)

    def save_metadata(self, metadata: ModelMetadata, path: Path) -> Path:
        metadata_path = MetadataWriter().save(metadata, path)
        logger.info(f"Saved model metadata: path={metadata_path}")
        return metadata_path

    def load_metadata(self, path: Path) -> ModelMetadata:
        return MetadataReader().load(path)
