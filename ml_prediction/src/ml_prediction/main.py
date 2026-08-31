import argparse
import logging
import sys
from collections.abc import Sequence

from ml_prediction.application.application import Application
from ml_prediction.config.settings import get_settings
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.evaluation.model_evaluator import ModelEvaluator
from ml_prediction.features.house_feature_model import HouseFeatureModel
from ml_prediction.inference.house_price_predictor import HousePricePredictor
from ml_prediction.presentation.prediction_presenter import PredictionPresenter
from ml_prediction.presentation.training_presenter import TrainingPresenter
from ml_prediction.training.house_price_trainer import HousePriceTrainer

PREDICTIONS = ("train", "predict")


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a machine learning application.")
    parser.add_argument("dataset", nargs="?", choices=DATASETS, help="Dataset name.")
    parser.add_argument("prediction", nargs="?", choices=PREDICTIONS, help="Operation to run.")
    return parser


def _create_house_application(settings, include_prediction: bool = True) -> Application:
    feature_model = HouseFeatureModel()
    dataset_service = Dataset(settings.data_dir / settings.dataset_filename, settings.dataset_name)
    predictor = None
    if include_prediction:
        predictor = HousePricePredictor(
            dataset_service.dataset_name,
            feature_model,
        )
    return Application(
        dataset_service,
        HousePriceTrainer(dataset_service),
        predictor,
    )


DATASET_COMPOSERS = {
    "house": _create_house_application,
}
DATASETS = tuple(DATASET_COMPOSERS)


def create_application(dataset: str, include_prediction: bool = True) -> Application:
    settings = get_settings(dataset)
    try:
        compose = DATASET_COMPOSERS[dataset]
    except KeyError as error:
        supported = ", ".join(sorted(DATASET_COMPOSERS))
        raise ValueError(
            f"Dataset '{dataset}' has no application composer. Supported datasets: {supported}"
        ) from error
    return compose(settings, include_prediction)


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
        training_output = application.train()
        TrainingPresenter().present(training_output)
        return

    prediction_output = application.predict()
    settings = get_settings(dataset)
    PredictionPresenter(settings.data_dir / settings.prediction_filename).present(prediction_output)


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
