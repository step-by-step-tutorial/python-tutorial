import pytest

from pyspark.sql import DataFrame, SparkSession

from dataset.definition import DataLakeEndpoint, MessagingEndpoint
from dataset.sale.config import SALE_DATASET
from service import spark_service as system_under_test

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

        actual = system_under_test.SparkService(
            session=given_session,
            datalake_endpoint=DataLakeEndpoint(bucket_name="bucket"),
            messaging_endpoint=MessagingEndpoint(
                channel_name=SALE_DATASET.get_endpoint("sale.kafka.listener", MessagingEndpoint).channel_name,
                bootstrap_servers="localhost:9092",
                starting_offsets="earliest",
            ),
        ).read_from_kafka()

        assert actual is given_dataframe
        assert given_session.readStream.format.call_count == 1
        assert given_stream_reader.option.call_count == 1
        assert given_option_one.option.call_count == 1
        assert given_option_two.option.call_count == 1
        assert given_option_three.option.call_count == 1
        assert given_option_four.load.call_count == 1
