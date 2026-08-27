import argparse
import logging
import sys
from collections.abc import Sequence

from data_platform.pipeline.data_pipeline import DataPipeline
from data_platform.pipeline.spark_pipeline import SparkPipeline
from data_platform.registry.bootstrap import initialize_registries
from data_platform.registry.dataset_registry import dataset_registry

logger = logging.getLogger(__name__)

PIPELINE_TYPES = ("inmemory", "spark")

initialize_registries()


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a data platform pipeline.")
    parser.add_argument("dataset", nargs="?", help="Dataset name, for example house.")
    parser.add_argument(
        "pipeline_type",
        nargs="?",
        choices=PIPELINE_TYPES,
        help="Pipeline type: inmemory or spark.",
    )
    return parser


def get_spark_dataset(dataset_name: str):
    from data_platform.domain.house.spark_dataset import spark_house_dataset
    from data_platform.domain.online_shopping.spark_dataset import spark_online_shopping_dataset

    datasets = {
        spark_house_dataset.name: spark_house_dataset,
        spark_online_shopping_dataset.name: spark_online_shopping_dataset,
    }
    try:
        return datasets[dataset_name.lower()]
    except KeyError as error:
        raise ValueError(f"Unsupported Spark dataset: {dataset_name}") from error


def get_dataset(dataset_name: str, pipeline_type: str):
    if pipeline_type == "inmemory":
        return dataset_registry.get_item(dataset_name.lower())
    return get_spark_dataset(dataset_name)


def run_pipeline(dataset_name: str, pipeline_type: str) -> None:
    dataset = get_dataset(dataset_name, pipeline_type)
    pipeline = DataPipeline(dataset) if pipeline_type == "inmemory" else SparkPipeline(dataset)
    logger.info("Running pipeline: dataset=%s type=%s", dataset_name, pipeline_type)
    pipeline.run()


def select_dataset() -> str | None:
    names = dataset_registry.names()
    if not names:
        raise RuntimeError("No datasets are registered.")

    print("Available datasets:")
    for index, name in enumerate(names, start=1):
        print(f"  {index}. {name}")
    print("  0. Exit")

    while True:
        selection = input("Select a dataset: ").strip().lower()
        if selection in {"0", "q", "quit", "exit"}:
            return None
        if selection.isdigit() and 1 <= int(selection) <= len(names):
            return names[int(selection) - 1]
        print(f"Select a number between 1 and {len(names)}, or 0 to exit.")


def select_pipeline_type() -> str | None:
    print("Available pipeline types:")
    for index, pipeline_type in enumerate(PIPELINE_TYPES, start=1):
        print(f"  {index}. {pipeline_type}")
    print("  0. Exit")

    while True:
        selection = input("Select a pipeline type: ").strip().lower()
        if selection in {"0", "q", "quit", "exit"}:
            return None
        if selection.isdigit() and 1 <= int(selection) <= len(PIPELINE_TYPES):
            return PIPELINE_TYPES[int(selection) - 1]
        print(f"Select a number between 1 and {len(PIPELINE_TYPES)}, or 0 to exit.")


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    args = create_parser().parse_args(argv)

    if (args.dataset is None) != (args.pipeline_type is None):
        raise SystemExit("dataset and pipeline_type must be provided together")

    if args.dataset is not None:
        run_pipeline(args.dataset, args.pipeline_type)
        return

    if not sys.stdin.isatty():
        raise RuntimeError("dataset name and pipeline type are required when standard input is not interactive.")

    dataset_name = select_dataset()
    if dataset_name is None:
        return

    pipeline_type = select_pipeline_type()
    if pipeline_type is not None:
        run_pipeline(dataset_name, pipeline_type)


if __name__ == "__main__":
    main()
