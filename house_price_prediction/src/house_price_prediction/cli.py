import logging

from house_price_prediction.application.application import Application
from house_price_prediction.config.settings import house_settings
from house_price_prediction.dataset.house_dataset import HouseDataset
from house_price_prediction.inference.house_price_predictor import HousePricePredictor
from house_price_prediction.inference.prediction_service import PredictionService
from house_price_prediction.presentation.prediction_presenter import PredictionPresenter
from house_price_prediction.presentation.training_presenter import TrainingPresenter
from house_price_prediction.repository.model_repository import ModelRepository
from house_price_prediction.training.house_price_trainer import HousePriceTrainer

logger = logging.getLogger(__name__)


def create_application() -> Application:
    model_repository = ModelRepository()
    prediction_service = PredictionService(
        house_settings,
        HousePricePredictor(
            house_settings.model_dir / "house_price_model.joblib",
            model_repository,
        ),
        HouseDataset(house_settings.data_dir / "house.csv"),
    )
    return Application(
        house_settings,
        HousePriceTrainer(house_settings, model_repository),
        prediction_service,
    )


application = create_application()


def train() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    result = application.train()
    TrainingPresenter().present(result)


def predict() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    result = application.predict()
    PredictionPresenter().present(result, house_settings.data_dir / "house_predictions.csv")


if __name__ == "__main__":
    train()
