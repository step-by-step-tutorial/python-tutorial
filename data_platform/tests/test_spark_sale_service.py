import pytest
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

from service import spark_sale_service as system_under_test


class TestReadSaleData:

    def test_should_read_and_validate_sale_data(self, mocker) -> None:
        # Given
        given_session = mocker.MagicMock(spec=SparkSession)
        given_path = "fake.csv"
        given_schema = StructType()
        given_dataframe = mocker.MagicMock(spec=DataFrame)

        given_session.read.option.return_value.schema.return_value.csv.return_value = given_dataframe

        mock_requires_column = mocker.patch.object(system_under_test, "requires_column")

        # When
        actual = system_under_test.read_data(given_session, given_path, given_schema)

        # Then
        assert actual is given_dataframe
        assert given_session.read.option.call_count == 1
        assert given_session.read.option.return_value.schema.call_count == 1
        assert given_session.read.option.return_value.schema.return_value.csv.call_count == 1
        assert mock_requires_column.call_count == 1

    def test_should_raise_error_when_session_is_none(self) -> None:
        # Given
        given_session = None
        given_path = "data.csv"
        given_schema = StructType()
        given_error_message = "Cannot read data because the Spark session is None."

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.read_data(given_session, given_path, given_schema)

        # Then
        assert str(actual.value) == given_error_message

    def test_should_raise_error_when_path_is_none(self, mocker) -> None:
        # Given
        given_session = mocker.MagicMock(spec=SparkSession)
        given_path = None
        given_schema = StructType()
        given_error_message = "Cannot read data because the input path is None."

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.read_data(given_session, given_path, given_schema)

        # Then
        assert str(actual.value) == given_error_message

    def test_should_raise_error_when_schema_is_none(self, mocker) -> None:
        # Given
        given_session = mocker.MagicMock(spec=SparkSession)
        given_path = "data.csv"
        given_schema = None
        given_error_message = "Cannot read data because the input schema is None."

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.read_data(given_session, given_path, given_schema)

        # Then
        assert str(actual.value) == given_error_message

    def test_should_propagate_error_when_csv_reading_fails(self, mocker) -> None:
        # Given
        given_session = mocker.MagicMock(spec=SparkSession)
        given_path = "missing.csv"
        given_schema = StructType()
        given_error_message = "CSV file not found"

        given_session.read.option.return_value.schema.return_value.csv.side_effect = FileNotFoundError(
            given_error_message
        )

        # When
        with pytest.raises(FileNotFoundError) as actual:
            system_under_test.read_data(given_session, given_path, given_schema)

        # Then
        assert str(actual.value) == given_error_message

    def test_should_propagate_error_when_required_columns_are_missing(self, mocker) -> None:
        # Given
        given_session = mocker.MagicMock(spec=SparkSession)
        given_path = "invalid.csv"
        given_schema = StructType()
        given_dataframe = mocker.MagicMock(spec=DataFrame)
        given_error_message = "Missing required columns"

        given_session.read.option.return_value.struct_type.return_value.csv.return_value = given_dataframe

        mocker.patch.object(
            system_under_test,
            "requires_column",
            side_effect=ValueError(given_error_message),
        )

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.read_data(given_session, given_path, given_schema)

        # Then
        assert str(actual.value) == given_error_message


class TestCleanSaleData:

    def test_should_call_cleaning_functions_with_expected_arguments(self, mocker) -> None:
        # Given
        given_dataframe = mocker.MagicMock(spec=DataFrame)
        given_order_date_column = mocker.MagicMock()
        given_quantity_column = mocker.MagicMock()
        given_unit_price_column = mocker.MagicMock()
        given_order_date_condition = mocker.MagicMock()
        given_quantity_condition = mocker.MagicMock()
        given_unit_price_condition = mocker.MagicMock()

        given_order_date_column.isNotNull.return_value = given_order_date_condition
        given_quantity_column.__gt__ = mocker.Mock(return_value=given_quantity_condition)
        given_unit_price_column.__ge__ = mocker.Mock(return_value=given_unit_price_condition)

        mock_remove_duplicates = mocker.patch.object(
            system_under_test,
            "remove_duplicates",
            return_value=given_dataframe,
        )
        mock_convert_numeric_column = mocker.patch.object(
            system_under_test,
            "convert_numeric_column",
            return_value=given_dataframe,
        )
        mock_fill_missing_by_group_average = mocker.patch.object(
            system_under_test,
            "fill_missing_by_group_average",
            return_value=given_dataframe,
        )
        mock_fill_missing_by_column_average = mocker.patch.object(
            system_under_test,
            "fill_missing_by_column_average",
            return_value=given_dataframe,
        )
        mock_convert_datetime_column = mocker.patch.object(
            system_under_test,
            "convert_datetime_column",
            return_value=given_dataframe,
        )
        mock_filter_dataframe = mocker.patch.object(
            system_under_test,
            "filter_dataframe",
            return_value=given_dataframe,
        )
        mocker.patch.object(
            system_under_test.sf,
            "col",
            side_effect=[
                given_order_date_column,
                given_quantity_column,
                given_unit_price_column,
            ],
        )

        # When
        actual = system_under_test.clean_data(given_dataframe)

        # Then
        assert actual is given_dataframe
        assert mock_remove_duplicates.call_count == 1
        assert mock_convert_numeric_column.call_count == 2
        assert mock_fill_missing_by_group_average.call_count == 1
        assert mock_fill_missing_by_column_average.call_count == 1
        assert mock_convert_datetime_column.call_count == 1
        assert mock_filter_dataframe.call_count == 1


class TestEnrichSaleData:

    def test_should_add_total_price_year_and_month_columns(self, mocker) -> None:
        # Given
        given_dataframe = mocker.MagicMock(spec=DataFrame)
        given_quantity_column = mocker.MagicMock()
        given_unit_price_column = mocker.MagicMock()
        given_total_price_column = mocker.MagicMock()
        given_rounded_total_price_column = mocker.MagicMock()
        given_year_column = mocker.MagicMock()
        given_month_column = mocker.MagicMock()

        given_quantity_column.__mul__ = mocker.Mock(return_value=given_total_price_column)
        given_dataframe.withColumn.return_value = given_dataframe

        mock_column = mocker.patch.object(
            system_under_test.sf,
            "col",
            side_effect=[
                given_quantity_column,
                given_unit_price_column,
            ],
        )
        mock_round = mocker.patch.object(
            system_under_test.sf,
            "round",
            return_value=given_rounded_total_price_column,
        )
        mock_year = mocker.patch.object(
            system_under_test.sf,
            "year",
            return_value=given_year_column,
        )
        mock_month = mocker.patch.object(
            system_under_test.sf,
            "month",
            return_value=given_month_column,
        )

        # When
        actual = system_under_test.enrich_data(given_dataframe)

        # Then
        assert actual is given_dataframe
        assert mock_column.call_count == 2
        assert mock_round.call_count == 1
        assert mock_year.call_count == 1
        assert mock_month.call_count == 1
        assert given_dataframe.withColumn.call_count == 3


class TestGetRevenueByCategory:

    def test_should_group_total_price_by_category(self, mocker) -> None:
        # Given
        given_dataframe = mocker.MagicMock(spec=DataFrame)
        given_expected_dataframe = mocker.MagicMock(spec=DataFrame)

        mock_sum_by_group = mocker.patch.object(
            system_under_test,
            "sum_by_group",
            return_value=given_expected_dataframe,
        )

        # When
        actual = system_under_test.get_revenue_by_category(given_dataframe)

        # Then
        assert actual is given_expected_dataframe
        assert mock_sum_by_group.call_count == 1


class TestGetRevenueByCountry:

    def test_should_group_total_price_by_country(self, mocker) -> None:
        # Given
        given_dataframe = mocker.MagicMock(spec=DataFrame)
        given_expected_dataframe = mocker.MagicMock(spec=DataFrame)

        mock_sum_by_group = mocker.patch.object(
            system_under_test,
            "sum_by_group",
            return_value=given_expected_dataframe,
        )

        # When
        actual = system_under_test.get_revenue_by_country(given_dataframe)

        # Then
        assert actual is given_expected_dataframe
        assert mock_sum_by_group.call_count == 1