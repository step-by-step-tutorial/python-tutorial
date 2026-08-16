import pytest

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

from dataset.sale.config import SALE_DATASET
from service.spark import batch_service as system_under_test

pytestmark = pytest.mark.unit


class TestReadStream:

    def test_should_read_stream_from_kafka_topic(self, mocker) -> None:
        given_session = mocker.MagicMock(spec=SparkSession)
        given_dataframe = mocker.MagicMock(spec=DataFrame)
        given_stream_reader = given_session.readStream.format.return_value
        given_option_one = given_stream_reader.option.return_value
        given_option_two = given_option_one.option.return_value
        given_option_three = given_option_two.option.return_value
        given_option_four = given_option_three.option.return_value
        given_option_four.load.return_value = given_dataframe

        mocker.patch.object(system_under_test, "create_session", return_value=given_session)

        actual = system_under_test.SparkBatchService().read_stream(
            SALE_DATASET.get_source("messaging").topic,
            "localhost:9092",
            "earliest",
        )

        assert actual is given_dataframe
        assert given_session.readStream.format.call_count == 1
        assert given_stream_reader.option.call_count == 1
        assert given_option_one.option.call_count == 1
        assert given_option_two.option.call_count == 1
        assert given_option_three.option.call_count == 1
        assert given_option_four.load.call_count == 1


class TestConvertStream:

    def test_should_validate_required_columns_from_function_arguments(self, mocker) -> None:
        given_dataframe = mocker.MagicMock(spec=DataFrame)
        given_schema = StructType()
        given_required_columns = {"order_id"}
        given_converted_dataframe = mocker.MagicMock(spec=DataFrame)
        given_converted_dataframe.columns = ["order_id"]

        mocker.patch.object(system_under_test.sf, "from_json", return_value=mocker.MagicMock())
        mocker.patch.object(system_under_test.sf, "col", return_value=mocker.MagicMock())
        given_dataframe.select.return_value.filter.return_value.select.return_value = given_converted_dataframe

        actual = system_under_test.SparkBatchService().convert_stream(
            dataframe=given_dataframe,
            schema=given_schema,
            required_columns=given_required_columns,
        )

        assert actual is given_converted_dataframe
