import logging

from ml_prediction.application.application import Application
from ml_prediction.config.settings import house_settings
from ml_prediction.dataset.house_dataset import HouseDataset
from ml_prediction.inference.house_price_predictor import HousePricePredictor
from ml_prediction.inference.prediction_service import PredictionService
from ml_prediction.presentation.prediction_presenter import PredictionPresenter
from ml_prediction.presentation.training_presenter import TrainingPresenter
from ml_prediction.repository.local_repository import LocalRepository
from ml_prediction.training.house_price_trainer import HousePriceTrainer

logger = logging.getLogger(__name__)


def create_application() -> Application:
    model_repository = LocalRepository()
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
        HousePriceTrainer(house_settings),
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
    PredictionPresenter(house_settings.data_dir / "house_predictions.csv").present(result)


if __name__ == "__main__":
    train()
