
from src.clickhouse_sales_repository import ClickHouseSalesRepository
from src.sale_warehouse_repository import SaleWarehouseRepository
from src.spark_postgres_sales_repository import (
    SparkPostgresSalesRepository,
)
from src.sale_postgres_repository import SalePostgresRepository
from src.spark_sales_data_cleaning_service import (
    SparkSalesDataCleaningService,
)
from src.sale_data_cleaning_service import SaleDataCleaningService


def test_legacy_cleaning_service_should_point_to_current_service():
    # Given
    given_legacy_service = SparkSalesDataCleaningService

    # When
    actual = given_legacy_service

    # Then
    assert actual is SaleDataCleaningService


def test_legacy_postgres_repository_should_point_to_current_repository():
    # Given
    given_legacy_repository = SparkPostgresSalesRepository

    # When
    actual = given_legacy_repository

    # Then
    assert actual is SalePostgresRepository


def test_legacy_warehouse_repository_should_point_to_current_repository():
    # Given
    given_legacy_repository = ClickHouseSalesRepository

    # When
    actual = given_legacy_repository

    # Then
    assert actual is SaleWarehouseRepository
