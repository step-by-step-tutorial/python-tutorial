from pathlib import Path

import pandas as pd
import pytest

from data_platform.domain.online_shopping.attribute import attribute
from data_platform.converter.value_converter import (
    convert_to_integer,
    convert_to_float,
    convert_to_optional_float,
    normalize_optional_text,
)
from data_platform.validators.validator_impl import RequiredColumnsValidator
from data_platform.util import file_utils


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
        actual = file_utils.read_text_file("database/house/truncate_stage.sql")

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


class TestPandasDataFrameModelUtils:

    def test_should_validate_required_columns(self) -> None:
        # Given
        dataframe = pd.DataFrame({attribute.order_id: [1]})

        # When / Then
        with pytest.raises(ValueError):
            RequiredColumnsValidator(frozenset({attribute.order_id, attribute.category})).validate(dataframe)

    def test_should_sum_by_group(self) -> None:
        # Given
        dataframe = pd.DataFrame(
            {
                attribute.category: ["A", "A", "B"],
                attribute.total_amount: [10.0, 20.0, 5.0],
            }
        )

        # When
        actual = dataframe.groupby(attribute.category, as_index=False)[attribute.total_amount].sum()
        actual = actual.rename(columns={attribute.total_amount: "revenue"})
        actual = actual.sort_values("revenue", ascending=False).reset_index(drop=True)

        # Then
        assert actual.iloc[0][attribute.category] == "A"
        assert actual.iloc[0]["revenue"] == 30.0

    def test_should_raise_attribute_error_for_unknown_attribute(self) -> None:
        with pytest.raises(AttributeError):
            _ = attribute.unknown_column
