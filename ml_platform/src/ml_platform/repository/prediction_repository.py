import logging
from pathlib import Path

from ml_platform.model.prediction_model import PredictionModel

logger = logging.getLogger(__name__)


class PredictionRepository:
    def save(self, path: Path, prediction: PredictionModel) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        prediction.to_dataframe().to_csv(path, index=False)
        logger.info("Saved predictions: path=%s %s", path, prediction.to_string())
        return path
