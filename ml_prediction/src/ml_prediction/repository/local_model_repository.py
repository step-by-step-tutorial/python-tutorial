import logging
from pathlib import Path
from typing import Any

import joblib

from ml_prediction.audit.data.metadata import Metadata
from ml_prediction.audit.metadata_service import MetadataService

logger = logging.getLogger(__name__)


class LocalModelRepository:
    def __init__(self):
        self._metadata_service = MetadataService()

    def save_model(self, path: Path, model: Any, metadata: Metadata):
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, path)
        self.save_metadata(metadata, path)
        logger.info(f"Saved model: path={path}")

    def load_model(self, path: Path) -> Any:
        logger.info(f"Loading model: path={path}")
        return joblib.load(path)

    def save_metadata(self, metadata: Metadata, path: Path):
        self._metadata_service.write(metadata, path)
        logger.info(f"Saved model metadata: path={path.with_suffix('.metadata.json')}")

    def load_metadata(self, path: Path) -> Metadata:
        return self._metadata_service.read(path)
