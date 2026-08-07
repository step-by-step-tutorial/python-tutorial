import logging

from pipeline import inmemory_auditable_pipeline, spark_based_streaming_pipeline, inmemory_pipeline, \
    spark_based_pipeline

logging.basicConfig(  level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Starting Sale ETL Platform")
    # inmemory_pipeline.run()
    # inmemory_auditable_pipeline.run()
    # spark_based_pipeline.run()
    # spark_based_streaming_pipeline.run()
    spark_based_streaming_pipeline.StreamingPipeline()

    logger.info("Sale ETL Platform finished")


if __name__ == "__main__":
    main()
