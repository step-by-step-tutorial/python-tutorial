import logging
from pathlib import Path

from ml_prediction.data_model.prediction_dto import PredictionDto
from ml_prediction.presentation.view import View

logger = logging.getLogger(__name__)


class PredictionView(View):
    def __init__(self, path: Path) -> None:
        self._path = path

    def render(self, dto: PredictionDto) -> Path:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        dto.dataframe.assign(**{dto.prediction_column: dto.predictions}).to_csv(self._path, index=False)
        logger.info(f"Prediction result: {dto.to_string()} output={self._path}")
        return self._path
