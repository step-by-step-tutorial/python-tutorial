import logging
from pipeline.inmemory_auditable_pipeline import InmemoryAuditablePipeline
from pipeline.inmemory_pipeline import InmemoryPipeline
from pipeline.spark_based_pipeline import SparkPipeline
from pipeline.spark_based_streaming_pipeline import SparkStreamingPipeline
logging.basicConfig(  level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Starting Sale ETL Platform")
    # SparkStreamingPipeline()
    # SparkPipeline()
    # InmemoryPipeline()
    InmemoryAuditablePipeline()
    logger.info("Sale ETL Platform finished")


if __name__ == "__main__":
    main()
