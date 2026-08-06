from pathlib import Path

import pandas as pd
import pytest
from pandas import DataFrame
from pandas.testing import assert_frame_equal
from pytest import MonkeyPatch

from app_config.dataframe_schema import SALE_COLUMNS
from service import csv_sale_service as system_under_test


@pytest.fixture
def dataframe() -> DataFrame:
    return pd.DataFrame(
        {
            SALE_COLUMNS.ORDER_ID: [1, 2, 3],
            SALE_COLUMNS.CUSTOMER_NAME: [
                "Ali Ahmadi",
                "John Smith",
                "Anna Müller",
            ],
            SALE_COLUMNS.PRODUCT_NAME: [
                "Laptop",
                "Mouse",
                "Keyboard",
            ],
            SALE_COLUMNS.CATEGORY: [
                "Electronics",
                "Accessories",
                "Accessories",
            ],
            SALE_COLUMNS.QUANTITY: [2.0, 3.0, 1.0],
            SALE_COLUMNS.UNIT_PRICE: [1000.0, 20.0, 50.0],
            SALE_COLUMNS.ORDER_DATE: [
                "2026-01-10",
                "2026-02-15",
                "2026-03-20",
            ],
            SALE_COLUMNS.COUNTRY: [
                "Iran",
                "United States",
                "Germany",
            ],
        }
    )


@pytest.fixture
def enriched_dataframe() -> DataFrame:
    return pd.DataFrame(
        {
            SALE_COLUMNS.ORDER_ID: [1, 2, 3, 4],
            SALE_COLUMNS.CATEGORY: [
                "Electronics",
                "Electronics",
                "Accessories",
                "Accessories",
            ],
            SALE_COLUMNS.COUNTRY: [
                "Iran",
                "Germany",
                "Iran",
                "Germany",
            ],
            SALE_COLUMNS.TOTAL_PRICE: [
                2000.0,
                1500.0,
                100.0,
                250.0,
            ],
        }
    )


class TestReadSaleDataCsv:

    def test_should_read_and_validate_sale_data(self, monkeypatch: MonkeyPatch, dataframe: DataFrame) -> None:
        # Given
        def mock_csv_to_dataframe(path: Path) -> DataFrame:
            return dataframe

        def mock_requires_column(df: DataFrame, columns: set[str]) -> None:
            pass

        monkeypatch.setattr(system_under_test, "csv_to_dataframe", mock_csv_to_dataframe)
        monkeypatch.setattr(system_under_test, "requires_column", mock_requires_column)

        given_path = Path("resources/fake.csv")

        # When
        actual = system_under_test.read_data(given_path)

        # Then
        assert actual is dataframe

    def test_should_propagate_error_when_csv_reading_fails(self, monkeypatch: MonkeyPatch) -> None:
        # Given
        def given_csv_to_dataframe(csv_path: Path) -> DataFrame:
            raise FileNotFoundError(given_error_message)

        monkeypatch.setattr(system_under_test, "csv_to_dataframe", given_csv_to_dataframe)

        given_csv_path = Path("resources/missing.csv")
        given_error_message = "CSV file not found"

        # When
        with pytest.raises(FileNotFoundError) as actual:
            system_under_test.read_data(given_csv_path)

        # Then
        assert str(actual.value) == given_error_message

    def test_should_propagate_error_when_required_columns_are_missing(
            self,
            monkeypatch: MonkeyPatch,
            dataframe: DataFrame
    ) -> None:
        # Given
        def mock_csv_to_dataframe(path: Path) -> DataFrame:
            return dataframe

        def mock_requires_column(df: DataFrame, columns: set[str]) -> None:
            raise ValueError(given_error_message)

        monkeypatch.setattr(system_under_test, "csv_to_dataframe", mock_csv_to_dataframe)
        monkeypatch.setattr(system_under_test, "requires_column", mock_requires_column)

        given_csv_path = Path("resources/invalid.csv")
        given_error_message = "Missing required columns"

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.read_data(given_csv_path)

        # Then
        assert str(actual.value) == given_error_message


class TestCleanSaleData:

    def test_should_call_cleaning_functions_with_expected_arguments(self, mocker, dataframe: DataFrame) -> None:
        # Given
        mock_remove_duplicates = mocker.patch.object(
            system_under_test, "remove_duplicates", return_value=dataframe)
        mock_convert_numeric_column = mocker.patch.object(
            system_under_test, "convert_numeric_column", return_value=dataframe
        )
        mock_fill_missing_by_group_average = mocker.patch.object(
            system_under_test, "fill_missing_by_group_average", return_value=dataframe
        )
        mock_fill_missing_by_column_average = mocker.patch.object(
            system_under_test, "fill_missing_by_column_average", return_value=dataframe
        )
        mock_convert_datetime_column = mocker.patch.object(
            system_under_test, "convert_datetime_column", return_value=dataframe
        )
        mock_reset_index = mocker.patch.object(
            system_under_test, "reset_index", return_value=dataframe
        )

        # When
        system_under_test.clean_data(dataframe)

        # Then
        assert mock_remove_duplicates.call_count == 1
        assert mock_convert_numeric_column.call_count == 2
        assert mock_fill_missing_by_group_average.call_count == 1
        assert mock_fill_missing_by_column_average.call_count == 1
        assert mock_convert_datetime_column.call_count == 1
        assert mock_reset_index.call_count == 1

    def test_should_not_modify_original_dataframe(self, mocker, dataframe: DataFrame) -> None:
        # Given
        given_original_dataframe = dataframe.copy(deep=True)
        given_copied_dataframe = dataframe.copy(deep=True)
        mocker.patch.object(given_original_dataframe, "copy", return_value=given_copied_dataframe)

        def input_output_dataframe(df: DataFrame, *args, **kwargs) -> DataFrame:
            return df

        mocker.patch.object(system_under_test, "remove_duplicates", side_effect=input_output_dataframe)
        mocker.patch.object(system_under_test, "convert_numeric_column", side_effect=input_output_dataframe)
        mocker.patch.object(system_under_test, "fill_missing_by_group_average", side_effect=input_output_dataframe)
        mocker.patch.object(system_under_test, "fill_missing_by_column_average", side_effect=input_output_dataframe)
        mocker.patch.object(system_under_test, "convert_datetime_column", side_effect=input_output_dataframe)
        mocker.patch.object(system_under_test, "reset_index", side_effect=input_output_dataframe)

        # When
        actual = system_under_test.clean_data(given_original_dataframe)

        # Then
        assert actual is given_copied_dataframe
        assert actual is not given_original_dataframe

    def test_should_filter_invalid_data(self) -> None:
        # Given
        given_dataframe = pd.DataFrame(
            {
                SALE_COLUMNS.ORDER_ID: [1, 2, 3, 4],
                SALE_COLUMNS.CUSTOMER_NAME: ["Ali Ahmadi", "John Smith", "Anna Müller", "Sara Mohammadi"],
                SALE_COLUMNS.PRODUCT_NAME: ["Laptop", "Mouse", "Keyboard", "Monitor"],
                SALE_COLUMNS.CATEGORY: ["Electronics", "Accessories", "Accessories", "Electronics"],
                SALE_COLUMNS.QUANTITY: [2.0, 0.0, 1.0, 2.0],
                SALE_COLUMNS.UNIT_PRICE: [1000.0, 20.0, -10.0, 300.0],
                SALE_COLUMNS.ORDER_DATE: ["2026-01-10", "2026-02-15", "2026-03-20", "invalid-date"],
                SALE_COLUMNS.COUNTRY: ["Iran", "United States", "Germany", "Iran"],
            }
        )

        # When
        actual = system_under_test.clean_data(given_dataframe)

        # Then
        assert len(actual) == 1
        assert actual.iloc[0][SALE_COLUMNS.ORDER_ID] == 1
        assert actual.index.tolist() == [0]


class TestEnrichSaleData:

    def test_should_calculate_total_price_year_and_month(self) -> None:
        # Given
        given_dataframe = pd.DataFrame(
            {
                SALE_COLUMNS.ORDER_ID: [1, 2],
                SALE_COLUMNS.QUANTITY: [2.0, 3.0],
                SALE_COLUMNS.UNIT_PRICE: [10.125, 20.555],
                SALE_COLUMNS.ORDER_DATE: pd.to_datetime(["2026-01-15", "2025-12-20"])
            }
        )

        given_expected_dataframe = given_dataframe.copy()
        given_expected_dataframe[SALE_COLUMNS.TOTAL_PRICE] = [20.25, 61.66]
        given_expected_dataframe[SALE_COLUMNS.YEAR] = pd.Series([2026, 2025], dtype="int32", )
        given_expected_dataframe[SALE_COLUMNS.MONTH] = pd.Series([1, 12], dtype="int32", )

        # When
        actual = system_under_test.enrich_data(given_dataframe)

        # Then
        assert_frame_equal(actual, given_expected_dataframe)

    def test_should_not_modify_original_dataframe(self) -> None:
        # Given
        given_original_dataframe = pd.DataFrame(
            {
                SALE_COLUMNS.QUANTITY: [2.0],
                SALE_COLUMNS.UNIT_PRICE: [10.0],
                SALE_COLUMNS.ORDER_DATE: pd.to_datetime(["2026-07-30"])
            }
        )

        # When
        actual = system_under_test.enrich_data(given_original_dataframe)

        # Then
        assert actual is not given_original_dataframe
        assert set(given_original_dataframe.columns) == {
            SALE_COLUMNS.QUANTITY,
            SALE_COLUMNS.UNIT_PRICE,
            SALE_COLUMNS.ORDER_DATE
        }
        assert set(actual.columns) == {
            SALE_COLUMNS.QUANTITY,
            SALE_COLUMNS.UNIT_PRICE,
            SALE_COLUMNS.ORDER_DATE,
            SALE_COLUMNS.TOTAL_PRICE,
            SALE_COLUMNS.YEAR,
            SALE_COLUMNS.MONTH
        }

    def test_should_return_empty_dataframe_with_derived_columns(self) -> None:
        # Given
        given_dataframe = pd.DataFrame(
            {
                SALE_COLUMNS.QUANTITY: pd.Series(dtype="float64"),
                SALE_COLUMNS.UNIT_PRICE: pd.Series(dtype="float64"),
                SALE_COLUMNS.ORDER_DATE: pd.Series(dtype="datetime64[ns]")
            }
        )

        # When
        actual = system_under_test.enrich_data(given_dataframe)

        # Then
        assert actual.empty
        assert set(actual.columns) == {
            SALE_COLUMNS.QUANTITY,
            SALE_COLUMNS.UNIT_PRICE,
            SALE_COLUMNS.ORDER_DATE,
            SALE_COLUMNS.TOTAL_PRICE,
            SALE_COLUMNS.YEAR,
            SALE_COLUMNS.MONTH
        }


class TestGetRevenueByCategory:

    def test_should_group_total_price_by_category(self, mocker, enriched_dataframe: DataFrame) -> None:
        # Given
        expected_dataframe = pd.DataFrame(
            {
                SALE_COLUMNS.CATEGORY: ["Electronics", "Accessories", ],
                SALE_COLUMNS.REVENUE: [3500.0, 350.0],
            }
        )

        mock_sum_by_group = mocker.patch.object(system_under_test, "sum_by_group", return_value=expected_dataframe)

        # When
        actual = system_under_test.get_revenue_by_category(enriched_dataframe)

        # Then
        assert actual is expected_dataframe
        assert mock_sum_by_group.call_count == 1


class TestGetRevenueByCountry:

    def test_should_group_total_price_by_country(self, mocker, enriched_dataframe: DataFrame) -> None:
        # Given
        expected_dataframe = pd.DataFrame(
            {
                SALE_COLUMNS.COUNTRY: ["Iran", "Germany"],
                SALE_COLUMNS.REVENUE: [2100.0, 1750.0],
            }
        )

        mock_sum_by_group = mocker.patch.object(system_under_test, "sum_by_group", return_value=expected_dataframe)

        # When
        actual = system_under_test.get_revenue_by_country(enriched_dataframe)

        # Then
        assert actual is expected_dataframe
        assert mock_sum_by_group.call_count == 1
