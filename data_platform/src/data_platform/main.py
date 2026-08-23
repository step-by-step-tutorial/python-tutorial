import logging
import sys
from importlib import import_module

from data_platform.config.main_settings import settings as main_settings
from data_platform.registry.dataset_registry import dataset_registry

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)

PIPELINES = {
    "inmemory": lambda dataset: import_module("data_platform.pipeline.inmemory_pipeline").InmemoryPipeline(dataset),
    "spark": lambda dataset: import_module("data_platform.pipeline.spark_pipeline").SparkPipeline(dataset),
    "spark_streaming": lambda dataset: import_module("data_platform.pipeline.spark_streaming_pipeline").SparkStreamingPipeline(dataset),
}

DATASETS = {
    "sale": "sale",
    "house": "house",
}

DATASET_OPTIONS = [
    ("1", "sale"),
    ("2", "house"),
]

PIPELINE_OPTIONS = [
    ("1", "inmemory"),
    ("2", "spark"),
    ("3", "spark_streaming"),
]


def run_pipeline(pipeline_type: str, dataset_name: str) -> None:
    if pipeline_type not in PIPELINES:
        raise ValueError(f"Unsupported pipeline type: {pipeline_type}")

    if dataset_name not in DATASETS:
        raise ValueError(f"Unsupported dataset: {dataset_name}")

    pipeline = PIPELINES[pipeline_type](dataset_registry.get_item(dataset_name))
    pipeline.run()


def main() -> None:
    if len(sys.argv) > 1:
        pipeline_type = sys.argv[1]
        dataset_name = sys.argv[2] if len(sys.argv) > 2 else main_settings.app.dataset_name
        run_pipeline(pipeline_type, dataset_name)
        return

    while True:
        print()
        print("Available datasets:")
        for command, dataset_name in DATASET_OPTIONS:
            print(f"{command}. {dataset_name}")
        print("0. exit")

        dataset_command = input("> ").strip()

        if dataset_command in {"0", "exit", "quit"}:
            return

        dataset_name = dict(DATASET_OPTIONS).get(dataset_command, dataset_command)

        if dataset_name not in DATASETS:
            logger.error("Unsupported dataset: %s", dataset_name)
            continue

        print()
        print("Available pipelines:")
        for command, pipeline_name in PIPELINE_OPTIONS:
            print(f"{command}. {pipeline_name}")
        print("0. back")

        pipeline_command = input("> ").strip()

        if pipeline_command in {"0", "back"}:
            continue

        if pipeline_command in {"exit", "quit"}:
            return

        pipeline_type = dict(PIPELINE_OPTIONS).get(pipeline_command, pipeline_command)

        try:
            run_pipeline(pipeline_type, dataset_name)
        except Exception as error:
            logger.exception(f"Failed to execute pipeline {pipeline_type} with dataset {dataset_name}: {error}")


if __name__ == "__main__":
    main()
