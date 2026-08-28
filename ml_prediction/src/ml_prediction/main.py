import argparse
import logging
import sys
from collections.abc import Sequence

from ml_prediction.application.application import Application
from ml_prediction.config.settings import house_settings
from ml_prediction.dataset.house_dataset import HouseDataset
from ml_prediction.inference.house_price_predictor import HousePricePredictor
from ml_prediction.inference.prediction_service import PredictionService
from ml_prediction.presentation.prediction_presenter import PredictionPresenter
from ml_prediction.presentation.training_presenter import TrainingPresenter
from ml_prediction.repository.local_model_repository import LocalModelRepository
from ml_prediction.reporting.report_service import ReportService
from ml_prediction.training.house_price_trainer import HousePriceTrainer

logger = logging.getLogger(__name__)

DATASETS = ("house",)
PREDICTIONS = ("train", "predict")


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a machine learning application.")
    parser.add_argument("dataset", nargs="?", choices=DATASETS, help="Dataset name.")
    parser.add_argument("prediction", nargs="?", choices=PREDICTIONS, help="Operation to run.")
    return parser


def create_application(dataset: str, include_prediction: bool = True) -> Application:
    if dataset != "house":
        raise ValueError(f"Unsupported dataset: {dataset}")

    report_service = ReportService(house_settings.report_dir)
    prediction_service = None
    if include_prediction:
        model_repository = LocalModelRepository()
        prediction_service = PredictionService(
            house_settings,
            HousePricePredictor(
                house_settings.model_dir / "house_price_model.joblib",
                model_repository,
            ),
            HouseDataset(house_settings.data_dir / "house.csv"),
            report_service,
        )
    return Application(
        house_settings,
        HousePriceTrainer(house_settings, report_service),
        prediction_service,
    )


def select_dataset() -> str | None:
    print("Available datasets:")
    for index, dataset in enumerate(DATASETS, start=1):
        print(f"  {index}. {dataset}")
    print("  0. Exit")

    while True:
        selection = input("Select a dataset: ").strip().lower()
        if selection in {"0", "q", "quit", "exit"}:
            return None
        if selection.isdigit() and 1 <= int(selection) <= len(DATASETS):
            return DATASETS[int(selection) - 1]
        print(f"Select a number between 1 and {len(DATASETS)}, or 0 to exit.")


def select_prediction() -> str | None:
    print("Available predictions:")
    for index, prediction in enumerate(PREDICTIONS, start=1):
        print(f"  {index}. {prediction}")
    print("  0. Exit")

    while True:
        selection = input("Select a prediction: ").strip().lower()
        if selection in {"0", "q", "quit", "exit"}:
            return None
        if selection.isdigit() and 1 <= int(selection) <= len(PREDICTIONS):
            return PREDICTIONS[int(selection) - 1]
        print(f"Select a number between 1 and {len(PREDICTIONS)}, or 0 to exit.")


def run(dataset: str, prediction: str) -> None:
    application = create_application(dataset, include_prediction=prediction == "predict")
    if prediction == "train":
        result = application.train()
        TrainingPresenter().present(result)
        return

    result = application.predict()
    PredictionPresenter(house_settings.data_dir / "house_predictions.csv").present(result)


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = create_parser().parse_args(argv)

    if (args.dataset is None) != (args.prediction is None):
        raise SystemExit("dataset and prediction must be provided together")

    if args.dataset is not None:
        run(args.dataset, args.prediction)
        return

    if not sys.stdin.isatty():
        raise RuntimeError("dataset and prediction are required when standard input is not interactive")

    dataset = select_dataset()
    if dataset is None:
        return

    prediction = select_prediction()
    if prediction is not None:
        run(dataset, prediction)


if __name__ == "__main__":
    main()
