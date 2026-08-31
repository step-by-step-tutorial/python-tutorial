import logging
from pathlib import Path

from ml_prediction.data_model.prediction_output import PredictionOutput
from ml_prediction.presentation.presenter import Presenter

logger = logging.getLogger(__name__)


class PredictionPresenter(Presenter):
    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def present(self, output: PredictionOutput) -> Path:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        output.dataframe.assign(
            **{output.prediction_column: output.predictions}
        ).to_csv(self.output_path, index=False)
        if output.predictions.empty or not output.predictions.map(
                lambda value: isinstance(value, (int, float))
        ).all():
            logger.info(
                "Prediction result: source=%s output=%s report=%s rows=%s prediction_column=%s",
                output.source_path,
                self.output_path,
                output.report_path,
                len(output.predictions),
                output.prediction_column,
            )
        else:
            logger.info(
                "Prediction result: source=%s output=%s report=%s rows=%s prediction_column=%s "
                "min=%.2f max=%.2f average=%.2f",
                output.source_path,
                self.output_path,
                output.report_path,
                len(output.predictions),
                output.prediction_column,
                output.predictions.min(),
                output.predictions.max(),
                output.predictions.mean(),
            )
        return self.output_path
