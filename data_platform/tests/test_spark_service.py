import pytest
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

from dataset.sale.config import SALE_DATASET
from service import spark_service as system_under_test


class TestReadSaleData:

    def test_should_read_and_validate_sale_data(self, mocker) -> None:
        # Given
        given_session = mocker.MagicMock(spec=SparkSession)
        given_path = "fake.csv"
        given_schema = StructType()
        given_dataframe = mocker.MagicMock(spec=DataFrame)

        given_session.read.option.return_value.schema.return_value.csv.return_value = given_dataframe

        mock_requires_column = mocker.patch.object(system_under_test, "requires_column")
        mocker.patch.object(system_under_test.spark_connection_factory, "create_connection", return_value=given_session)

        # When
        actual = system_under_test.SparkService(SALE_DATASET).read_csv(given_path, given_schema)

        # Then
        assert actual is given_dataframe
        assert mock_requires_column.call_count == 1

    def test_should_raise_error_when_path_is_none(self, mocker) -> None:
        # Given
        given_schema = StructType()
        given_error_message = "Value of file_path should not be None or empty"

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.SparkService(SALE_DATASET).read_csv(None, given_schema)

        # Then
        assert str(actual.value) == given_error_message
