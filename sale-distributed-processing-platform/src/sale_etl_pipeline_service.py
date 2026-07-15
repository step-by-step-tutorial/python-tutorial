
import logging

from pyspark.sql import SparkSession

from src import config
from src.sale_data_cleaning_service import SaleDataCleaningService
from src.sale_data_lake_repository import SaleDataLakeRepository
from src.sale_data_transformation_service import SaleDataTransformationService
from src.sale_postgres_repository import SalePostgresRepository
from src.sale_schema import SALE_SCHEMA
from src.sale_warehouse_repository import SaleWarehouseRepository


logger = logging.getLogger(__name__)


class SaleEtlPipelineService:
    def __init__(
        self,
        sale_spark_session: SparkSession,
    ) -> None:
        self.sale_spark_session = sale_spark_session
        self.sale_data_cleaning_service = SaleDataCleaningService()
        self.sale_data_transformation_service = SaleDataTransformationService()
        self.sale_postgres_repository = SalePostgresRepository()
        self.sale_data_lake_repository = SaleDataLakeRepository()
        self.sale_warehouse_repository = SaleWarehouseRepository()

    def run_sale_etl_pipeline(self) -> None:
        logger.info(
            "Reading sale data from %s",
            config.SALE_INPUT_CSV_PATH,
        )

        sale_dataframe = (
            self.sale_spark_session
            .read
            .option("header", "true")
            .schema(SALE_SCHEMA)
            .csv(config.SALE_INPUT_CSV_PATH)
        )

        logger.info("Cleaning sale data")
        cleaned_sale_dataframe = (
            self.sale_data_cleaning_service
            .clean_sale_data(sale_dataframe)
        )

        logger.info("Transforming sale data")
        transformed_sale_dataframe = (
            self.sale_data_transformation_service
            .transform_sale_data(cleaned_sale_dataframe)
        )

        transformed_sale_dataframe.cache()

        try:
            logger.info("Storing sale data in PostgreSQL")
            self.sale_postgres_repository.replace_sale_data(
                transformed_sale_dataframe
            )

            logger.info("Storing curated sale data in data lake")
            self.sale_data_lake_repository.replace_curated_sale_data(
                transformed_sale_dataframe
            )

            logger.info("Building sale warehouse dataframe")
            sale_warehouse_dataframe = (
                self.sale_data_transformation_service
                .build_sale_warehouse_dataframe(
                    transformed_sale_dataframe
                )
            )

            logger.info("Storing sale fact data in warehouse")
            self.sale_warehouse_repository.replace_sale_fact(
                sale_warehouse_dataframe
            )

            logger.info(
                "Revenue by category:\n%s",
                self.sale_warehouse_repository.get_revenue_by_category(),
            )
            logger.info(
                "Revenue by country:\n%s",
                self.sale_warehouse_repository.get_revenue_by_country(),
            )
            logger.info("Sale ETL pipeline completed successfully")
        finally:
            transformed_sale_dataframe.unpersist()
