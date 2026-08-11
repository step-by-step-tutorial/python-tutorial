import logging

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


def main() -> None:
    PIPELINES[ec.PIPELINE_TYPE](get_dataset(ec.DATASET_NAME))


if __name__ == "__main__":
    main()
