import logging

from house_price_prediction.config.settings import settings
from house_price_prediction.dataset.house_dataset import HouseDataset
from house_price_prediction.inference.predictor import HousePricePredictor
from house_price_prediction.repository.datalake_repository import DataLakeRepository
from house_price_prediction.training.trainer import HousePriceTrainer

logger = logging.getLogger(__name__)


def train() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    result = HousePriceTrainer(settings).train()
    logger.info(
        "Training result: model=%s baseline_mae=%.2f validation_mae=%.2f test_mae=%.2f test_r2=%.4f",
        result.model_path,
        result.baseline_metrics.mean_absolute_error,
        result.validation_metrics.mean_absolute_error,
        result.model_metrics.mean_absolute_error,
        result.model_metrics.r2_score,
    )


def predict() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    dataset_path = settings.data_dir / "house.csv"
    DataLakeRepository(settings.data_lake).download_latest_csv(dataset_path)
    dataframe = HouseDataset(dataset_path).load()
    predictions = HousePricePredictor(settings.model_dir / "house_price_model.joblib").predict(dataframe)
    output_path = settings.data_dir / "house_predictions.csv"
    dataframe.assign(predicted_total_price=predictions).to_csv(output_path, index=False)
    logger.info("Predictions saved: path=%s rows=%s", output_path, len(dataframe))


if __name__ == "__main__":
    train()
