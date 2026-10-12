import argparse
import logging
import sys
from collections.abc import Sequence

from data_platform.config.pipeline_type import PipelineType
from data_platform.pipeline.inmemory_pipeline import InmemoryPipeline
from data_platform.pipeline.pipeline import Pipeline
from data_platform.registry.bootstrap import initialize_registries
from data_platform.registry.dataset_registry import dataset_registry

logger = logging.getLogger(__name__)

PIPELINE_TYPES = tuple(PipelineType)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a data platform pipeline.")
    parser.add_argument("dataset", nargs="?", help="Dataset name, for example house.")
    parser.add_argument(
        "pipeline_type",
        nargs="?",
        choices=PIPELINE_TYPES,
        type=PipelineType,
        help="Pipeline type: inmemory or spark.",
    )
    return parser


def create_pipeline(dataset_name: str, pipeline_type: PipelineType) -> Pipeline:
    dataset = dataset_registry.create_dataset(dataset_name, pipeline_type)
    if pipeline_type == PipelineType.SPARK:
        from data_platform.pipeline.spark_pipeline import SparkPipeline
        return SparkPipeline(dataset)
    return InmemoryPipeline(dataset)


def run_pipeline(dataset_name: str, pipeline_type: PipelineType) -> None:
    pipeline = create_pipeline(dataset_name, pipeline_type)
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


def select_pipeline_type() -> PipelineType | None:
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
    initialize_registries()

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
