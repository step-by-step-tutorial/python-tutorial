import pytest

pytest.importorskip("pyspark")

from pyspark.sql import SparkSession  # noqa: E402

from data_platform.ingestion.spark_csv_file_ingestor import SparkCsvFileIngestor  # noqa: E402
from data_platform.ingestion.spark_kafka_ingestor import SparkKafkaIngestor  # noqa: E402
from data_platform.model.endpoint_model import MessagingEndpointModel  # noqa: E402


class TestSparkCsvFileIngestor:

    def test_should_delegate_to_spark_reader(self, mocker) -> None:
        given_spark = mocker.MagicMock(spec=SparkSession)
        given_dataframe = mocker.Mock()
        given_spark.read.option.return_value.schema.return_value.csv.return_value = given_dataframe
        ingestor = SparkCsvFileIngestor(session=given_spark)

        actual = ingestor.ingest(file_path="/tmp/sample.csv", schema={"schema": "value"})

        assert actual is given_dataframe
        assert given_spark.read.option.call_count == 1
        assert given_spark.read.option.call_args.args == ("header", "true")
        assert given_spark.read.option.return_value.schema.call_count == 1
        assert given_spark.read.option.return_value.schema.call_args.args[0] == {"schema": "value"}
        assert given_spark.read.option.return_value.schema.return_value.csv.call_count == 1
        assert given_spark.read.option.return_value.schema.return_value.csv.call_args.args[0].endswith("sample.csv")


class TestStreamingChannelIngestor:

    def test_should_read_stream_from_topic(self, mocker) -> None:
        given_spark = mocker.Mock()
        given_dataframe = mocker.Mock()
        given_stream_reader = given_spark.read.format.return_value
        given_option_one = given_stream_reader.option.return_value
        given_option_two = given_option_one.option.return_value
        given_option_three = given_option_two.option.return_value
        given_option_four = given_option_three.option.return_value
        given_option_five = given_option_four.option.return_value
        given_option_five.load.return_value = given_dataframe
        given_dataframe.select.return_value = given_dataframe
        given_column = mocker.Mock()
        given_column.cast.return_value = "value-as-string"
        mock_col = mocker.patch("data_platform.ingestion.spark_kafka_ingestor.sf.col", return_value=given_column)
        mock_from_json = mocker.patch("data_platform.ingestion.spark_kafka_ingestor.sf.from_json")
        mock_from_json.return_value.alias.return_value = "payload"

        ingestor = SparkKafkaIngestor(
            endpoint=MessagingEndpointModel(
                connection_name="house.kafka.listener",
                channel_name="example-events",
                bootstrap_servers="localhost:9092",
                starting_offsets="earliest",
            ),
            session=given_spark,
            schema={"schema": "value"},
        )

        actual = ingestor.ingest()

        assert actual is given_dataframe
        assert mock_col.call_count == 1
        assert mock_from_json.call_count == 1
        assert given_spark.read.format.call_count == 1
        assert given_stream_reader.option.call_count == 1
        assert given_option_one.option.call_count == 1
        assert given_option_two.option.call_count == 1
        assert given_option_three.option.call_count == 1
        assert given_option_five.load.call_count == 1
        assert given_dataframe.select.call_count == 2
