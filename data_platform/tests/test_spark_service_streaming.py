from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

from dataset.sale.config import SALE_DATASET
from service import spark_service as system_under_test


class TestReadStream:

    def test_should_read_stream_from_kafka_topic(self, mocker) -> None:
        # Given
        given_session = mocker.MagicMock(spec=SparkSession)
        given_dataframe = mocker.MagicMock(spec=DataFrame)
        given_stream_reader = given_session.readStream.format.return_value
        given_option_one = given_stream_reader.option.return_value
        given_option_two = given_option_one.option.return_value
        given_option_three = given_option_two.option.return_value
        given_option_four = given_option_three.option.return_value
        given_option_four.load.return_value = given_dataframe

        mocker.patch.object(system_under_test.spark_connection_factory, "create_connection", return_value=given_session)

        # When
        actual = system_under_test.SparkService(SALE_DATASET).read_stream(SALE_DATASET.streaming.topic)

        # Then
        assert actual is given_dataframe
        assert given_session.readStream.format.call_count == 1
        assert given_stream_reader.option.call_count == 1
        assert given_option_one.option.call_count == 1
        assert given_option_two.option.call_count == 1
        assert given_option_three.option.call_count == 1
        assert given_option_four.load.call_count == 1


class TestConvertStream:

    def test_should_validate_required_columns_from_function_arguments(self, mocker) -> None:
        # Given
        given_dataframe = mocker.MagicMock(spec=DataFrame)
        given_schema = StructType()
        given_required_columns = {"order_id"}
        given_converted_dataframe = mocker.MagicMock(spec=DataFrame)

        mocker.patch.object(system_under_test.sf, "from_json", return_value=mocker.MagicMock())
        mocker.patch.object(system_under_test.sf, "col", return_value=mocker.MagicMock())
        mock_requires_column = mocker.patch.object(system_under_test, "requires_column", return_value=None)
        given_dataframe.select.return_value.filter.return_value.select.return_value = given_converted_dataframe

        # When
        actual = system_under_test.SparkService(SALE_DATASET).convert_stream(
            dataframe=given_dataframe,
            schema=given_schema,
            required_columns=given_required_columns,
        )

        # Then
        assert actual is given_converted_dataframe
        assert mock_requires_column.call_count == 1
