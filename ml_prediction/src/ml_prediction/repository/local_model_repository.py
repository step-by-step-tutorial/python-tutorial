import logging
from pathlib import Path
from typing import Any

import joblib

from ml_prediction.audit.metadata_service import MetadataService
from ml_prediction.audit.data.metadata import Metadata

logger = logging.getLogger(__name__)


class LocalModelRepository:
    def save(self, model: Any, path: Path, metadata: Metadata | None = None) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, path)
        if metadata is not None:
            self.save_metadata(metadata, path)
        logger.info(f"Saved model: path={path}")
        return path

    def load(self, path: Path) -> Any:
        logger.info(f"Loading model: path={path}")
        return joblib.load(path)

    def save_metadata(self, metadata: Metadata, path: Path) -> Path:
        metadata_path = MetadataService().write(metadata, path)
        logger.info(f"Saved model metadata: path={metadata_path}")
        return metadata_path

    def load_metadata(self, path: Path) -> Metadata:
        return MetadataService().read(path)
