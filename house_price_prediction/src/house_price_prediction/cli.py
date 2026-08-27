import logging

from house_price_prediction.config.settings import house_settings
from house_price_prediction.dataset.house_dataset import HouseDataset
from house_price_prediction.inference.prediction_service import PredictionService
from house_price_prediction.inference.house_price_predictor import HousePricePredictor
from house_price_prediction.presentation.prediction_presenter import PredictionPresenter
from house_price_prediction.presentation.training_presenter import TrainingPresenter
from house_price_prediction.training.house_price_trainer import HousePriceTrainer

logger = logging.getLogger(__name__)


def train() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    result = HousePriceTrainer(house_settings).train()
    TrainingPresenter().present(result)


def predict() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    dataset_path = house_settings.data_dir / "house.csv"
    result = PredictionService(
        house_settings,
        HousePricePredictor(house_settings.model_dir / "house_price_model.joblib"),
        HouseDataset(dataset_path),
    ).predict()
    PredictionPresenter().present(result, house_settings.data_dir / "house_predictions.csv")


if __name__ == "__main__":
    train()
