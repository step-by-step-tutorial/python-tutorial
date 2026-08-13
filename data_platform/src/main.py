import logging
import sys

from app_config import env_config as ec
from dataset.registry import get_dataset
from pipeline.inmemory_auditable_pipeline import InmemoryAuditablePipeline
from pipeline.inmemory_pipeline import InmemoryPipeline
from pipeline.spark_based_pipeline import SparkPipeline
from pipeline.spark_based_streaming_pipeline import SparkStreamingPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)

PIPELINES = {
    "inmemory": InmemoryPipeline,
    "inmemory_auditable": InmemoryAuditablePipeline,
    "spark": SparkPipeline,
    "spark_streaming": SparkStreamingPipeline,
}

DATASETS = {
    "sale": "sale",
    "house": "house",
}


def run_pipeline(pipeline_type: str, dataset_name: str) -> None:
    if pipeline_type not in PIPELINES:
        raise ValueError(f"Unsupported pipeline type: {pipeline_type}")

    if dataset_name not in DATASETS:
        raise ValueError(f"Unsupported dataset: {dataset_name}")

    pipeline = PIPELINES[pipeline_type](get_dataset(dataset_name))
    pipeline.run()


def main() -> None:
    if len(sys.argv) > 1:
        pipeline_type = sys.argv[1]
        dataset_name = sys.argv[2] if len(sys.argv) > 2 else ec.DATASET_NAME
        run_pipeline(pipeline_type, dataset_name)
        return

    while True:
        print()
        print("Available datasets:")
        print("1. sale")
        print("2. house")
        print("0. exit")

        dataset_command = input("> ").strip()

        if dataset_command in {"0", "exit", "quit"}:
            return

        dataset_name = {
            "1": "sale",
            "2": "house",
        }.get(dataset_command, dataset_command)

        if dataset_name not in DATASETS:
            logger.error("Unsupported dataset: %s", dataset_name)
            continue

        print()
        print("Available pipelines:")
        print("1. inmemory")
        print("2. inmemory_auditable")
        print("3. spark")
        print("4. spark_streaming")
        print("0. back")

        pipeline_command = input("> ").strip()

        if pipeline_command in {"0", "back"}:
            continue

        if pipeline_command in {"exit", "quit"}:
            return

        pipeline_type = {
            "1": "inmemory",
            "2": "inmemory_auditable",
            "3": "spark",
            "4": "spark_streaming",
        }.get(pipeline_command, pipeline_command)

        try:
            run_pipeline(pipeline_type, dataset_name)
        except Exception as error:
            logger.exception(f"Failed to execute pipeline {pipeline_type} with dataset {dataset_name}: {error}")


if __name__ == "__main__":
    main()
