import logging
from pathlib import Path

from house_price_prediction.inference.prediction_service import PredictionOutput

logger = logging.getLogger(__name__)


class PredictionPresenter:
    def present(self, result: PredictionOutput, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result.dataframe.assign(predicted_total_price=result.predictions).to_csv(output_path, index=False)
        logger.info(
            "Prediction result: source=%s output=%s rows=%s min=%.2f max=%.2f average=%.2f",
            result.source_path,
            output_path,
            len(result.predictions),
            result.predictions.min(),
            result.predictions.max(),
            result.predictions.mean(),
        )
        return output_path
