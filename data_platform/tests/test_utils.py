from pathlib import Path

import pandas as pd
import pytest

from dataframe.validation import require_columns
from dataset.sale.model import SALE_COLUMNS
from util import csv_utils, file_utils, pandas_dataframe_utils


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
        assert csv_utils.convert_to_integer("12") == 12

    def test_should_return_none_for_blank_optional_float(self) -> None:
        assert csv_utils.convert_to_optional_float(" ") is None

    def test_should_normalize_optional_text(self) -> None:
        assert csv_utils.normalize_optional_text("  hello  ") == "hello"


class TestPandasDataframeUtils:

    def test_should_require_columns(self) -> None:
        # Given
        dataframe = pd.DataFrame({SALE_COLUMNS.ORDER_ID: [1]})

        # When / Then
        with pytest.raises(ValueError):
            require_columns(dataframe, frozenset({SALE_COLUMNS.ORDER_ID, SALE_COLUMNS.CATEGORY}))

    def test_should_sum_by_group(self) -> None:
        # Given
        dataframe = pd.DataFrame(
            {
                SALE_COLUMNS.CATEGORY: ["A", "A", "B"],
                SALE_COLUMNS.TOTAL_PRICE: [10.0, 20.0, 5.0],
            }
        )

        # When
        actual = pandas_dataframe_utils.sum_by_group(
            dataframe,
            SALE_COLUMNS.CATEGORY,
            SALE_COLUMNS.TOTAL_PRICE,
            SALE_COLUMNS.REVENUE,
        )

        # Then
        assert actual.iloc[0][SALE_COLUMNS.CATEGORY] == "A"
        assert actual.iloc[0][SALE_COLUMNS.REVENUE] == 30.0
