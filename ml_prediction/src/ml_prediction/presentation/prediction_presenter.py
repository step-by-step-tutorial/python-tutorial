import logging
from pathlib import Path

from ml_prediction.inference.prediction_service import PredictionOutput
from ml_prediction.presentation.presenter import Presenter

logger = logging.getLogger(__name__)


class PredictionPresenter(Presenter):
    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def present(self, prediction_output: PredictionOutput) -> Path:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        prediction_output.dataframe.assign(
            predicted_total_price=prediction_output.predictions
        ).to_csv(self.output_path, index=False)
        logger.info(
            "Prediction result: source=%s output=%s report=%s rows=%s min=%.2f max=%.2f average=%.2f",
            prediction_output.source_path,
            self.output_path,
            prediction_output.report_path,
            len(prediction_output.predictions),
            prediction_output.predictions.min(),
            prediction_output.predictions.max(),
            prediction_output.predictions.mean(),
        )
        return self.output_path
