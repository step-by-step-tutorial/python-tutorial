import logging
from pathlib import Path

from ml_prediction.inference.prediction_service import PredictionOutput
from ml_prediction.presentation.presenter import Presenter

logger = logging.getLogger(__name__)


class PredictionPresenter(Presenter):
    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def present(self, result: PredictionOutput) -> Path:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        result.dataframe.assign(predicted_total_price=result.predictions).to_csv(self.output_path, index=False)
        logger.info(
            "Prediction result: source=%s output=%s rows=%s min=%.2f max=%.2f average=%.2f",
            result.source_path,
            self.output_path,
            len(result.predictions),
            result.predictions.min(),
            result.predictions.max(),
            result.predictions.mean(),
        )
        return self.output_path
