import logging

from pipeline import spark_sale_data_pipeline, pandas_sale_data_pipeline, kafka_spark_sale_pipeline

logging.basicConfig(  level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Starting Sale ETL Platform")
    kafka_spark_sale_pipeline.run()
    # spark_sale_data_pipeline.run()
    # pandas_sale_data_pipeline.run()
    logger.info("Sale ETL Platform finished")


if __name__ == "__main__":
    main()
