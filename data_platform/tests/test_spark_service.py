import pytest
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

from service.spark import batch_service as system_under_test

pytestmark = pytest.mark.unit


class TestReadSaleData:

    def test_should_read_and_validate_sale_data(self, mocker) -> None:
        given_session = mocker.MagicMock(spec=SparkSession)
        given_path = "fake.csv"
        given_schema = StructType()
        given_dataframe = mocker.MagicMock(spec=DataFrame)

        given_session.read.option.return_value.schema.return_value.csv.return_value = given_dataframe

        mocker.patch.object(system_under_test, "create_session", return_value=given_session)

        actual = system_under_test.SparkBatchService().read_csv(given_path, given_schema)

        assert actual is given_dataframe

    def test_should_raise_error_when_path_is_none(self, mocker) -> None:
        given_schema = StructType()

        with pytest.raises(ValueError):
            system_under_test.SparkBatchService().read_csv(None, given_schema)
