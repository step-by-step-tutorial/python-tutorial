import logging
from pathlib import Path
from typing import Any

import joblib

logger = logging.getLogger(__name__)


class LocalRepository:
    def save(self, model: Any, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, path)
        logger.info("Saved model: path=%s", path)
        return path

    def load(self, path: Path) -> Any:
        logger.info("Loading model: path=%s", path)
        return joblib.load(path)
