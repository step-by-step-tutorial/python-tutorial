from pathlib import Path
from unittest.mock import call

import pandas as pd
import pytest
from pandas import DataFrame
from pandas.testing import assert_frame_equal

from app_config.sale_schema import SALE_COLUMNS, SALE_REQUIRED_COLUMNS
from service import csv_sale_service


@pytest.fixture
def given_dataframe() -> DataFrame:
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
def given_transformed_sale_dataframe() -> DataFrame:
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

    def test_should_read_and_validate_sale_data(
            self,
            monkeypatch: pytest.MonkeyPatch,
            given_dataframe: DataFrame,
    ) -> None:
        # Given
        given_csv_path = Path("resources/sale_data.csv")
        monkeypatch.setattr(csv_sale_service, "read_csv_file", lambda csv_path: given_dataframe)

        validated_arguments: dict[str, object] = {}

        def given_validate_columns(dataframe: DataFrame, required_columns: set[str]) -> None:
            validated_arguments["dataframe"] = dataframe
            validated_arguments["required_columns"] = required_columns

        monkeypatch.setattr(csv_sale_service, "validate_columns", given_validate_columns)

        # When
        actual = csv_sale_service.read_sale_data_csv(given_csv_path)

        # Then
        assert actual is given_dataframe
        assert validated_arguments["dataframe"] is given_dataframe
        assert validated_arguments["required_columns"] == SALE_REQUIRED_COLUMNS

    def test_should_propagate_error_when_csv_reading_fails(self, monkeypatch: pytest.MonkeyPatch, ) -> None:
        # Given
        given_csv_path = Path("resources/missing.csv")
        given_error_message = "CSV file not found"

        def given_read_csv_file(csv_path: Path) -> DataFrame:
            raise FileNotFoundError(given_error_message)

        monkeypatch.setattr(csv_sale_service, "read_csv_file", given_read_csv_file)

        # When
        with pytest.raises(FileNotFoundError) as actual:
            csv_sale_service.read_sale_data_csv(given_csv_path)

        # Then
        assert str(actual.value) == given_error_message

    def test_should_propagate_error_when_required_columns_are_missing(
            self,
            monkeypatch: pytest.MonkeyPatch,
            given_dataframe: DataFrame,
    ) -> None:
        # Given
        given_csv_path = Path("resources/invalid_sale_data.csv")
        given_error_message = "Missing required columns"

        monkeypatch.setattr(csv_sale_service, "read_csv_file", lambda csv_path: given_dataframe)

        def given_validate_columns(dataframe: DataFrame, required_columns: set[str]) -> None:
            raise ValueError(given_error_message)

        monkeypatch.setattr(csv_sale_service, "validate_columns", given_validate_columns)

        # When
        with pytest.raises(ValueError) as actual:
            csv_sale_service.read_sale_data_csv(given_csv_path)

        # Then
        assert str(actual.value) == given_error_message


class TestCleanSaleData:

    def test_should_call_cleaning_functions_with_expected_arguments(self, mocker, given_dataframe: DataFrame) -> None:
        # Given
        given_df_removing_duplicates = (given_dataframe.copy())
        given_df_quantity_conversion = (given_dataframe.copy())
        given_df_price_conversion = (given_dataframe.copy())
        given_df_group_average = (given_dataframe.copy())
        given_df_column_average = (given_dataframe.copy())
        given_df_date_conversion = (given_dataframe.copy())
        given_expected_dataframe = given_dataframe.copy()

        given_df_date_conversion[SALE_COLUMNS.ORDER_DATE] = pd.to_datetime(
            given_df_date_conversion[SALE_COLUMNS.ORDER_DATE])

        given_remove_duplicates = mocker.patch.object(
            csv_sale_service,
            "remove_duplicates",
            return_value=given_df_removing_duplicates,
        )
        given_convert_numeric_column = mocker.patch.object(
            csv_sale_service,
            "convert_numeric_column",
            side_effect=[
                given_df_quantity_conversion,
                given_df_price_conversion,
            ],
        )
        given_fill_missing_by_group_average = mocker.patch.object(
            csv_sale_service,
            "fill_missing_by_group_average",
            return_value=given_df_group_average
        )
        given_fill_missing_by_column_average = mocker.patch.object(
            csv_sale_service,
            "fill_missing_by_column_average",
            return_value=given_df_column_average
        )
        given_convert_datetime_column = mocker.patch.object(
            csv_sale_service,
            "convert_datetime_column",
            return_value=given_df_date_conversion
        )
        given_reset_index = mocker.patch.object(csv_sale_service, "reset_index", return_value=given_expected_dataframe)

        # When
        actual = csv_sale_service.clean_sale_data(given_dataframe)

        # Then
        assert actual is given_expected_dataframe

        given_remove_duplicates.assert_called_once()
        remove_duplicates_arguments = given_remove_duplicates.call_args.args
        assert_frame_equal(remove_duplicates_arguments[0], given_dataframe)
        assert remove_duplicates_arguments[1] == SALE_COLUMNS.ORDER_ID

        assert given_convert_numeric_column.call_args_list == [
            call(given_df_removing_duplicates, SALE_COLUMNS.QUANTITY, default_value=1.0),
            call(given_df_quantity_conversion, SALE_COLUMNS.UNIT_PRICE),
        ]

        given_fill_missing_by_group_average.assert_called_once_with(
            given_df_price_conversion,
            SALE_COLUMNS.CATEGORY,
            SALE_COLUMNS.UNIT_PRICE
        )

        given_fill_missing_by_column_average.assert_called_once_with(given_df_group_average, SALE_COLUMNS.UNIT_PRICE)

        given_convert_datetime_column.assert_called_once_with(given_df_column_average, SALE_COLUMNS.ORDER_DATE)

        given_reset_index.assert_called_once()
        reset_index_arguments = given_reset_index.call_args.kwargs

        assert reset_index_arguments["dataframe"] is given_df_date_conversion

        actual_conditions = reset_index_arguments["conditions"]

        assert len(actual_conditions) == 3
        assert actual_conditions[0].tolist() == [True, True, True]
        assert actual_conditions[1].tolist() == [True, True, True]
        assert actual_conditions[2].tolist() == [True, True, True]

    def test_should_not_modify_original_dataframe(self, mocker, given_dataframe: DataFrame) -> None:
        # Given
        given_original_dataframe = given_dataframe.copy(deep=True)

        def given_return_dataframe(dataframe: DataFrame, *args, **kwargs) -> DataFrame:
            return dataframe

        mocker.patch.object(csv_sale_service, "remove_duplicates", side_effect=given_return_dataframe)
        mocker.patch.object(csv_sale_service, "convert_numeric_column", side_effect=given_return_dataframe)
        mocker.patch.object(csv_sale_service, "fill_missing_by_group_average", side_effect=given_return_dataframe)
        mocker.patch.object(csv_sale_service, "fill_missing_by_column_average", side_effect=given_return_dataframe)

        def given_convert_datetime_column(dataframe: DataFrame, column: str) -> DataFrame:
            dataframe[column] = pd.to_datetime(dataframe[column])
            return dataframe

        mocker.patch.object(csv_sale_service, "convert_datetime_column", side_effect=given_convert_datetime_column)
        mocker.patch.object(csv_sale_service, "reset_index", side_effect=lambda dataframe, conditions: dataframe)

        # When
        actual = csv_sale_service.clean_sale_data(given_dataframe)

        # Then
        assert actual is not given_dataframe
        assert_frame_equal(given_dataframe, given_original_dataframe, )

    def test_should_filter_rows_with_invalid_values(self, mocker, ) -> None:
        # Given
        given_dataframe = pd.DataFrame(
            {
                SALE_COLUMNS.ORDER_ID: [1, 2, 3, 4],
                SALE_COLUMNS.CUSTOMER_NAME: [
                    "Ali Ahmadi",
                    "John Smith",
                    "Anna Müller",
                    "Sara Mohammadi",
                ],
                SALE_COLUMNS.PRODUCT_NAME: [
                    "Laptop",
                    "Mouse",
                    "Keyboard",
                    "Monitor",
                ],
                SALE_COLUMNS.CATEGORY: [
                    "Electronics",
                    "Accessories",
                    "Accessories",
                    "Electronics",
                ],
                SALE_COLUMNS.QUANTITY: [2.0, 0.0, 1.0, 2.0],
                SALE_COLUMNS.UNIT_PRICE: [
                    1000.0,
                    20.0,
                    -10.0,
                    300.0,
                ],
                SALE_COLUMNS.ORDER_DATE: [
                    "2026-01-10",
                    "2026-02-15",
                    "2026-03-20",
                    "invalid-date",
                ],
                SALE_COLUMNS.COUNTRY: [
                    "Iran",
                    "United States",
                    "Germany",
                    "Iran",
                ],
            }
        )

        mocker.patch.object(
            csv_sale_service,
            "remove_duplicates",
            side_effect=lambda dataframe, column: dataframe,
        )
        mocker.patch.object(
            csv_sale_service,
            "convert_numeric_column",
            side_effect=lambda dataframe, column, **kwargs: dataframe,
        )
        mocker.patch.object(
            csv_sale_service,
            "fill_missing_by_group_average",
            side_effect=lambda dataframe, *args: dataframe,
        )
        mocker.patch.object(
            csv_sale_service,
            "fill_missing_by_column_average",
            side_effect=lambda dataframe, *args: dataframe,
        )

        def given_convert_datetime_column(
                dataframe: DataFrame,
                column: str,
        ) -> DataFrame:
            dataframe[column] = pd.to_datetime(
                dataframe[column],
                errors="coerce",
            )
            return dataframe

        def given_reset_index(
                dataframe: DataFrame,
                conditions: list[pd.Series],
        ) -> DataFrame:
            combined_condition = conditions[0]

            for condition in conditions[1:]:
                combined_condition &= condition

            return dataframe.loc[
                combined_condition
            ].reset_index(drop=True)

        mocker.patch.object(
            csv_sale_service,
            "convert_datetime_column",
            side_effect=given_convert_datetime_column,
        )
        mocker.patch.object(
            csv_sale_service,
            "reset_index",
            side_effect=given_reset_index,
        )

        # When
        actual = csv_sale_service.clean_sale_data(given_dataframe)

        # Then
        assert len(actual) == 1
        assert actual.iloc[0][SALE_COLUMNS.ORDER_ID] == 1
        assert actual.index.tolist() == [0]


class TestTransformSaleData:

    def test_should_calculate_total_price_year_and_month(
            self,
    ) -> None:
        # Given
        given_dataframe = pd.DataFrame(
            {
                SALE_COLUMNS.ORDER_ID: [1, 2],
                SALE_COLUMNS.QUANTITY: [2.0, 3.0],
                SALE_COLUMNS.UNIT_PRICE: [10.125, 20.555],
                SALE_COLUMNS.ORDER_DATE: pd.to_datetime(
                    ["2026-01-15", "2025-12-20"]
                ),
            }
        )

        given_expected_dataframe = given_dataframe.copy()
        given_expected_dataframe[SALE_COLUMNS.TOTAL_PRICE] = [20.25, 61.66, ]
        given_expected_dataframe[SALE_COLUMNS.YEAR] = pd.Series([2026, 2025], dtype="int32", )
        given_expected_dataframe[SALE_COLUMNS.MONTH] = pd.Series([1, 12], dtype="int32", )

        # When
        actual = csv_sale_service.transform_sale_data(given_dataframe)

        # Then
        assert_frame_equal(actual, given_expected_dataframe)

    def test_should_not_modify_original_dataframe(self) -> None:
        # Given
        given_dataframe = pd.DataFrame(
            {
                SALE_COLUMNS.QUANTITY: [2.0],
                SALE_COLUMNS.UNIT_PRICE: [10.0],
                SALE_COLUMNS.ORDER_DATE: pd.to_datetime(
                    ["2026-07-30"]
                ),
            }
        )
        given_original_dataframe = given_dataframe.copy(deep=True)

        # When
        actual = csv_sale_service.transform_sale_data(
            given_dataframe
        )

        # Then
        assert actual is not given_dataframe
        assert_frame_equal(
            given_dataframe,
            given_original_dataframe,
        )
        assert SALE_COLUMNS.TOTAL_PRICE not in given_dataframe.columns
        assert SALE_COLUMNS.YEAR not in given_dataframe.columns
        assert SALE_COLUMNS.MONTH not in given_dataframe.columns

    def test_should_return_empty_dataframe_with_derived_columns(
            self,
    ) -> None:
        # Given
        given_dataframe = pd.DataFrame(
            {
                SALE_COLUMNS.QUANTITY: pd.Series(dtype="float64"),
                SALE_COLUMNS.UNIT_PRICE: pd.Series(dtype="float64"),
                SALE_COLUMNS.ORDER_DATE: pd.Series(
                    dtype="datetime64[ns]"
                ),
            }
        )

        # When
        actual = csv_sale_service.transform_sale_data(
            given_dataframe
        )

        # Then
        assert actual.empty
        assert SALE_COLUMNS.TOTAL_PRICE in actual.columns
        assert SALE_COLUMNS.YEAR in actual.columns
        assert SALE_COLUMNS.MONTH in actual.columns


class TestGetRevenueByCategory:

    def test_should_group_total_price_by_category(
            self,
            mocker,
            given_transformed_sale_dataframe: DataFrame,
    ) -> None:
        # Given
        given_expected_dataframe = pd.DataFrame(
            {
                SALE_COLUMNS.CATEGORY: [
                    "Electronics",
                    "Accessories",
                ],
                "revenue": [3500.0, 350.0],
            }
        )

        given_sum_by_group = mocker.patch.object(
            csv_sale_service,
            "sum_by_group",
            return_value=given_expected_dataframe,
        )

        # When
        actual = csv_sale_service.get_revenue_by_category(
            given_transformed_sale_dataframe
        )

        # Then
        assert actual is given_expected_dataframe
        given_sum_by_group.assert_called_once_with(
            given_transformed_sale_dataframe,
            SALE_COLUMNS.CATEGORY,
            original_field=SALE_COLUMNS.TOTAL_PRICE,
            alias_field="revenue",
        )


class TestGetRevenueByCountry:

    def test_should_group_total_price_by_country(
            self,
            mocker,
            given_transformed_sale_dataframe: DataFrame,
    ) -> None:
        # Given
        given_expected_dataframe = pd.DataFrame(
            {
                SALE_COLUMNS.COUNTRY: ["Iran", "Germany"],
                "revenue": [2100.0, 1750.0],
            }
        )

        given_sum_by_group = mocker.patch.object(
            csv_sale_service,
            "sum_by_group",
            return_value=given_expected_dataframe,
        )

        # When
        actual = csv_sale_service.get_revenue_by_country(
            given_transformed_sale_dataframe
        )

        # Then
        assert actual is given_expected_dataframe
        given_sum_by_group.assert_called_once_with(
            given_transformed_sale_dataframe,
            SALE_COLUMNS.COUNTRY,
            original_field=SALE_COLUMNS.TOTAL_PRICE,
            alias_field="revenue",
        )
