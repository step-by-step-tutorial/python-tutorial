import argparse
import logging
import sys
from collections.abc import Sequence

from ml_prediction.config.dataset_profiles import DATASET_PROFILES
from ml_prediction.config.operation import Operation
from ml_prediction.inference.predictor import Predictor
from ml_prediction.model.settings_model import SettingsModel
from ml_prediction.training.trainer import Trainer

DATASETS = tuple(DATASET_PROFILES)
OPERATIONS = tuple(Operation)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train or run a machine learning model.")
    parser.add_argument("dataset", nargs="?", choices=DATASETS, help="Dataset name.")
    parser.add_argument("operation", nargs="?", choices=OPERATIONS, type=Operation, help="Operation to run.")
    parser.add_argument("--search", action="store_true", help="Search hyperparameters before saving the model.")
    return parser


def run(dataset_name: str, operation: Operation, search_enabled: bool = False) -> None:
    settings = SettingsModel.from_env(DATASET_PROFILES[dataset_name], search_enabled=search_enabled)
    if operation == Operation.TRAIN:
        Trainer(settings).train()
    else:
        Predictor(settings).predict()


def select(title: str, options: Sequence[str]) -> str | None:
    print(f"Available {title}s:")
    for index, option in enumerate(options, start=1):
        print(f"  {index}. {option}")
    print("  0. Exit")

    while True:
        selection = input(f"Select a {title}: ").strip().lower()
        if selection in {"0", "q", "quit", "exit"}:
            return None
        if selection.isdigit() and 1 <= int(selection) <= len(options):
            return options[int(selection) - 1]
        print(f"Select a number between 1 and {len(options)}, or 0 to exit.")


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    args = create_parser().parse_args(argv)

    if (args.dataset is None) != (args.operation is None):
        raise SystemExit("dataset and operation must be provided together")

    if args.dataset is not None:
        run(args.dataset, args.operation, args.search)
        return

    if not sys.stdin.isatty():
        raise RuntimeError("dataset and operation are required when standard input is not interactive")

    dataset_name = select("dataset", DATASETS)
    if dataset_name is None:
        return

    operation = select("operation", OPERATIONS)
    if operation is not None:
        run(dataset_name, Operation(operation), args.search)


if __name__ == "__main__":
    main()
