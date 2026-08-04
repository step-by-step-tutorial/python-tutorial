from datetime import date

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import DateType, DoubleType, IntegerType, StringType, StructField, StructType

from app_config.env_config import resolve, RESOURCES_DIR
from app_config.dataframe_schema import SALE_COLUMNS, SCHEMA
from service import spark_sale_service as system_under_test

APP_NAME = "Test Application"
MASTER_URL = "local[*]"
DRIVER_HOST = "127.0.0.1"
DRIVER_BIND_ADDRESS = "127.0.0.1"


@pytest.fixture(scope="session")
def spark_session() -> SparkSession:
    session = SparkSession.builder \
        .appName(APP_NAME) \
        .master(MASTER_URL) \
        .config("spark.driver.host", DRIVER_HOST) \
        .config("spark.driver.bindAddress", DRIVER_BIND_ADDRESS) \
        .getOrCreate()

    yield session
    session.stop()


class TestReadSaleDataIntegration:

    def test_should_read_sale_data(self, spark_session: SparkSession) -> None:
        # Given
        given_path = resolve(RESOURCES_DIR) / "test/test_data.csv"

        # When
        actual = system_under_test.read_data(session=spark_session, path=str(given_path), schema=SCHEMA)

        # Then
        assert actual.count() == 1000

    def test_should_read_sale_data_with_expected_schema(self, spark_session: SparkSession) -> None:
        # Given
        given_path = resolve(RESOURCES_DIR) / "test/test_data.csv"
        given_expected_schema = [(field.name, field.dataType) for field in SCHEMA.fields]

        # When
        actual = system_under_test.read_data(session=spark_session, path=str(given_path), schema=SCHEMA)
        actual_schema = [(field.name, field.dataType) for field in actual.schema.fields]

        # Then
        assert actual_schema == given_expected_schema

    def test_should_raise_error_when_required_columns_are_missing(self, spark_session: SparkSession) -> None:
        # Given
        given_path = resolve(RESOURCES_DIR) / "test/invalid_test_data.csv"
        given_schema = StructType([
            StructField(SALE_COLUMNS.ORDER_ID, IntegerType(), True),
            StructField(SALE_COLUMNS.CUSTOMER_NAME, StringType(), True),
        ])

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.read_data(session=spark_session, path=str(given_path), schema=given_schema)

        # Then
        assert "Missing required columns:" in str(actual.value)


class TestCleanSaleDataIntegration:

    def test_should_filter_invalid_data(self, spark_session: SparkSession) -> None:
        # Given
        given_dataframe = spark_session.createDataFrame([
            (1, "Ali Ahmadi", "Laptop", "Electronics", 2.0, 1000.0, "2026-01-10", "Iran"),
            (2, "John Smith", "Mouse", "Accessories", 0.0, 20.0, "2026-02-15", "United States"),
            (3, "Anna Müller", "Keyboard", "Accessories", 1.0, -10.0, "2026-03-20", "Germany"),
            (4, "Sara Mohammadi", "Monitor", "Electronics", 2.0, 300.0, "invalid-date", "Iran"),
        ], SCHEMA)

        # When
        actual = system_under_test.clean_data(given_dataframe)

        # Then
        assert actual.count() == 1
        assert actual.first()[SALE_COLUMNS.ORDER_ID] == 1


class TestEnrichSaleDataIntegration:

    def test_should_calculate_total_price_year_and_month(self, spark_session: SparkSession) -> None:
        # Given
        given_schema = StructType([
            StructField(SALE_COLUMNS.ORDER_ID, IntegerType(), True),
            StructField(SALE_COLUMNS.QUANTITY, DoubleType(), True),
            StructField(SALE_COLUMNS.UNIT_PRICE, DoubleType(), True),
            StructField(SALE_COLUMNS.ORDER_DATE, DateType(), True),
        ])

        given_dataframe = spark_session.createDataFrame([
            (1, 2.0, 10.125, date(2026, 1, 15)),
            (2, 3.0, 20.555, date(2025, 12, 20)),
        ], given_schema)

        # When
        actual = system_under_test.enrich_data(given_dataframe)
        actual_rows = actual.orderBy(SALE_COLUMNS.ORDER_ID).collect()

        # Then
        assert actual_rows[0][SALE_COLUMNS.TOTAL_PRICE] == 20.25
        assert actual_rows[0][SALE_COLUMNS.YEAR] == 2026
        assert actual_rows[0][SALE_COLUMNS.MONTH] == 1
        assert actual_rows[1][SALE_COLUMNS.TOTAL_PRICE] == 61.67
        assert actual_rows[1][SALE_COLUMNS.YEAR] == 2025
        assert actual_rows[1][SALE_COLUMNS.MONTH] == 12

    def test_should_not_modify_original_dataframe(self, spark_session: SparkSession) -> None:
        # Given
        given_schema = StructType([
            StructField(SALE_COLUMNS.QUANTITY, DoubleType(), True),
            StructField(SALE_COLUMNS.UNIT_PRICE, DoubleType(), True),
            StructField(SALE_COLUMNS.ORDER_DATE, DateType(), True),
        ])

        given_original_dataframe = spark_session.createDataFrame([(2.0, 10.0, date(2026, 7, 30))], given_schema)
        given_original_columns = given_original_dataframe.columns

        # When
        actual = system_under_test.enrich_data(given_original_dataframe)

        # Then
        assert actual is not given_original_dataframe
        assert given_original_dataframe.columns == given_original_columns
        assert set(actual.columns) == {
            SALE_COLUMNS.QUANTITY,
            SALE_COLUMNS.UNIT_PRICE,
            SALE_COLUMNS.ORDER_DATE,
            SALE_COLUMNS.TOTAL_PRICE,
            SALE_COLUMNS.YEAR,
            SALE_COLUMNS.MONTH,
        }

    def test_should_return_empty_dataframe_with_derived_columns(self, spark_session: SparkSession) -> None:
        # Given
        given_schema = StructType([
            StructField(SALE_COLUMNS.QUANTITY, DoubleType(), True),
            StructField(SALE_COLUMNS.UNIT_PRICE, DoubleType(), True),
            StructField(SALE_COLUMNS.ORDER_DATE, DateType(), True),
        ])

        given_dataframe = spark_session.createDataFrame([], given_schema)

        # When
        actual = system_under_test.enrich_data(given_dataframe)

        # Then
        assert actual.count() == 0
        assert set(actual.columns) == {
            SALE_COLUMNS.QUANTITY,
            SALE_COLUMNS.UNIT_PRICE,
            SALE_COLUMNS.ORDER_DATE,
            SALE_COLUMNS.TOTAL_PRICE,
            SALE_COLUMNS.YEAR,
            SALE_COLUMNS.MONTH,
        }
