
import logging

from src.sale_etl_pipeline_service import SaleEtlPipelineService
from src.sale_spark_session_service import SaleSparkSessionService


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(name)s - "
        "%(message)s"
    ),
)

logger = logging.getLogger(__name__)


def run_sale_etl_pipeline() -> None:
    logger.info("Starting Sale ETL Platform")

    sale_spark_session_service = SaleSparkSessionService()
    sale_spark_session = (
        sale_spark_session_service
        .create_sale_spark_session()
    )

    try:
        sale_etl_pipeline_service = SaleEtlPipelineService(
            sale_spark_session=sale_spark_session
        )
        sale_etl_pipeline_service.run_sale_etl_pipeline()
    finally:
        logger.info("Stopping Spark session")
        sale_spark_session.stop()

    logger.info("Sale ETL Platform finished")


def main() -> None:
    run_sale_etl_pipeline()


if __name__ == "__main__":
    main()
