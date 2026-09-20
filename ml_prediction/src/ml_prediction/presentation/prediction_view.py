import logging
from pathlib import Path

from ml_prediction.data_model.prediction import Prediction
from ml_prediction.presentation.view import View

logger = logging.getLogger(__name__)


class PredictionView(View):
    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def render(self, data: Prediction) -> Path:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        data.dataframe.assign(
            **{data.prediction_column: data.predictions}
        ).to_csv(self.output_path, index=False)
        if data.predictions.empty or not data.predictions.map(
                lambda value: isinstance(value, (int, float))
        ).all():
            logger.info(
                "Prediction result: source=%s output=%s audit=%s rows=%s prediction_column=%s",
                data.source_path,
                self.output_path,
                data.audit_path,
                len(data.predictions),
                data.prediction_column,
            )
        else:
            logger.info(
                "Prediction result: source=%s output=%s audit=%s rows=%s prediction_column=%s "
                "min=%.2f max=%.2f average=%.2f",
                data.source_path,
                self.output_path,
                data.audit_path,
                len(data.predictions),
                data.prediction_column,
                data.predictions.min(),
                data.predictions.max(),
                data.predictions.mean(),
            )
        return self.output_path
