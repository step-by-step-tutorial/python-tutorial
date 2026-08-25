from pyspark.sql import DataFrame, SparkSession

from data_platform.domain.sale.dataset import sale_dataset
from data_platform.model.endpoints import MessagingEndpoint, DataLakeEndpoint
from data_platform.service import spark_streaming_service as system_under_test


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

        actual = system_under_test.SparkStreamingService(
            session=given_session,
            messaging_endpoint=MessagingEndpoint(
                channel_name=sale_dataset.get_endpoint("sale.kafka.listener", MessagingEndpoint).channel_name,
                bootstrap_servers="localhost:9092",
                starting_offsets="earliest",
            ),
            data_lake_endpoint=DataLakeEndpoint(bucket_name="bucket"),
        ).find()

        assert actual is given_dataframe
        assert given_session.readStream.format.call_count == 1
        assert given_stream_reader.option.call_count == 1
        assert given_option_one.option.call_count == 1
        assert given_option_two.option.call_count == 1
        assert given_option_three.option.call_count == 1
        assert given_option_four.load.call_count == 1

    def test_should_write_stream_through_foreach_batch(self, mocker) -> None:
        given_dataframe = mocker.MagicMock(spec=DataFrame)
        given_batch = mocker.Mock()
        given_stream_writer = given_dataframe.writeStream
        given_writer = given_stream_writer.foreachBatch.return_value
        given_writer.option.return_value = given_writer
        given_writer.trigger.return_value = given_writer
        given_writer.start_pipeline.return_value = mocker.Mock()
        service = system_under_test.SparkStreamingService(
            session=mocker.MagicMock(spec=SparkSession),
            messaging_endpoint=MessagingEndpoint(channel_name="topic", bootstrap_servers="localhost:9092"),
            data_lake_endpoint=DataLakeEndpoint(bucket_name="bucket"),
        )
        mock_append_batch = mocker.patch.object(service, "save_batch")

        service.save_stream(given_dataframe, "raw/path", "checkpoint/path")

        batch_handler = given_stream_writer.foreachBatch.call_args.args[0]
        batch_handler(given_batch, 0)
        assert mock_append_batch.call_args.args == (given_batch, "raw/path")
        assert given_writer.option.call_args.args == ("checkpointLocation", "checkpoint/path")
        assert given_writer.trigger.call_count == 1
        assert given_writer.start_pipeline.call_count == 1


