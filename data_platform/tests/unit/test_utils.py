from pathlib import Path

import pandas as pd
import pytest

from data_platform.sale.attribute import SALE_ATTRIBUTE
from data_platform.converter.pandas_converter import sum_by_group
from data_platform.converter.value_converter import (
    convert_to_integer,
    convert_to_float,
    convert_to_optional_float,
    normalize_optional_text,
)
from data_platform.validation.dataframe_validator import validate_required_columns
from data_platform.util import csv_utils, file_utils


class TestFileUtils:

    def test_should_read_csv_rows_and_call_consumer_once_per_row(self, tmp_path: Path, mocker) -> None:
        # Given
        csv_path = tmp_path / "example.csv"
        csv_path.write_text("id,name\n1,A\n2,B\n", encoding="utf-8")
        consumer = mocker.Mock()

        # When
        actual = file_utils.read_csv_file(str(csv_path), consumer)

        # Then
        assert actual == 2
        assert consumer.call_count == 2

    def test_should_read_text_file(self) -> None:
        # When
        actual = file_utils.read_text_file("database/sale/truncate_stage.sql")

        # Then
        assert "TRUNCATE" in actual.upper()


class TestCsvUtils:

    def test_should_convert_integer_value(self) -> None:
        assert convert_to_integer("12") == 12

    def test_should_convert_comma_formatted_float_value(self) -> None:
        assert convert_to_float(" 3,310,000,000 ") == 3310000000.0

    def test_should_return_none_for_blank_optional_float(self) -> None:
        assert convert_to_optional_float(" ") is None

    def test_should_normalize_optional_text(self) -> None:
        assert normalize_optional_text("  hello  ") == "hello"


class TestPandasDataFrameDefinitionUtils:

    def test_should_validate_required_columns(self) -> None:
        # Given
        dataframe = pd.DataFrame({SALE_ATTRIBUTE.ORDER_ID: [1]})

        # When / Then
        with pytest.raises(ValueError):
            validate_required_columns(dataframe, frozenset({SALE_ATTRIBUTE.ORDER_ID, SALE_ATTRIBUTE.CATEGORY}))

    def test_should_sum_by_group(self) -> None:
        # Given
        dataframe = pd.DataFrame(
            {
                SALE_ATTRIBUTE.CATEGORY: ["A", "A", "B"],
                SALE_ATTRIBUTE.TOTAL_PRICE: [10.0, 20.0, 5.0],
            }
        )

        # When
        actual = sum_by_group(
            dataframe,
            SALE_ATTRIBUTE.CATEGORY,
            SALE_ATTRIBUTE.TOTAL_PRICE,
            SALE_ATTRIBUTE.REVENUE,
        )

        # Then
        assert actual.iloc[0][SALE_ATTRIBUTE.CATEGORY] == "A"
        assert actual.iloc[0][SALE_ATTRIBUTE.REVENUE] == 30.0

    def test_should_raise_attribute_error_for_unknown_attribute(self) -> None:
        with pytest.raises(AttributeError):
            _ = SALE_ATTRIBUTE.unknown_column
