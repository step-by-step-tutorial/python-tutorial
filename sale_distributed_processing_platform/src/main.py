import logging

from pipeline.sale_data_pipeline import SaleDataPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Starting Sale ETL Platform")

    try:
        pipeline = SaleDataPipeline()
        pipeline.run()
    finally:
        logger.info("Stopping Spark session")

    logger.info("Sale ETL Platform finished")


if __name__ == "__main__":
    main()
