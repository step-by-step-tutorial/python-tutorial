import pytest
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

from dataset.definition import DataLakeEndpoint, MessagingEndpoint
from service import spark_service as system_under_test

pytestmark = pytest.mark.unit


class TestReadSaleData:

    def test_should_read_and_validate_sale_data(self, mocker) -> None:
        given_session = mocker.MagicMock(spec=SparkSession)
        given_path = "fake.csv"
        given_schema = StructType()
        given_dataframe = mocker.MagicMock(spec=DataFrame)

        given_session.read.option.return_value.schema.return_value.csv.return_value = given_dataframe
        actual = system_under_test.SparkService(
            session=given_session,
            datalake_endpoint=DataLakeEndpoint(bucket_name="bucket"),
            messaging_endpoint=MessagingEndpoint(channel_name="topic", bootstrap_servers="localhost:9092"),
        ).read_csv(given_path, given_schema)

        assert actual is given_dataframe

    def test_should_raise_error_when_path_is_none(self, mocker) -> None:
        given_schema = StructType()

        with pytest.raises(ValueError):
            system_under_test.SparkService(
                session=mocker.MagicMock(spec=SparkSession),
                datalake_endpoint=DataLakeEndpoint(bucket_name="bucket"),
                messaging_endpoint=MessagingEndpoint(channel_name="topic", bootstrap_servers="localhost:9092"),
            ).read_csv(None, given_schema)


class TestAppendBatchToObjectStorage:

    def test_should_persist_batch_before_appending(self, mocker) -> None:
        given_session = mocker.MagicMock(spec=SparkSession)
        given_dataframe = mocker.MagicMock(spec=DataFrame)
        given_dataframe.isEmpty.return_value = False
        given_persisted = mocker.Mock()
        given_context = mocker.MagicMock()
        given_context.__enter__.return_value = given_persisted
        given_context.__exit__.return_value = None

        service = system_under_test.SparkService(
            session=given_session,
            datalake_endpoint=DataLakeEndpoint(bucket_name="bucket"),
            messaging_endpoint=MessagingEndpoint(channel_name="topic", bootstrap_servers="localhost:9092"),
        )
        mock_persisted_dataframes = mocker.patch(
            "service.spark_service.persisted_dataframes",
            return_value=given_context,
        )
        mock_append = mocker.patch.object(service, "append_to_object_storage")

        service.append_batch_to_object_storage(given_dataframe, "cleaned/path")

        assert mock_persisted_dataframes.call_count == 1
        assert given_dataframe.persist.call_count == 1
        assert given_persisted.append.call_count == 1
        assert given_persisted.append.call_args.args == (given_dataframe.persist.return_value,)
        assert mock_append.call_count == 1
        assert mock_append.call_args.kwargs["dataframe"] is given_dataframe.persist.return_value
        assert mock_append.call_args.kwargs["path"] == "cleaned/path"


class TestAppendStreamToObjectStorage:

    def test_should_write_stream_through_foreach_batch(self, mocker) -> None:
        given_session = mocker.MagicMock(spec=SparkSession)
        given_dataframe = mocker.MagicMock(spec=DataFrame)
        given_batch = mocker.Mock()
        given_stream_writer = given_dataframe.writeStream
        given_writer = given_stream_writer.foreachBatch.return_value
        given_writer.option.return_value = given_writer
        given_writer.trigger.return_value = given_writer
        given_writer.start.return_value = mocker.Mock()

        service = system_under_test.SparkService(
            session=given_session,
            datalake_endpoint=DataLakeEndpoint(bucket_name="bucket"),
            messaging_endpoint=MessagingEndpoint(channel_name="topic", bootstrap_servers="localhost:9092"),
        )
        mock_append_batch = mocker.patch.object(service, "append_batch_to_object_storage")

        service.append_stream_to_object_storage(given_dataframe, "raw/path", "checkpoint/path")

        assert given_stream_writer.foreachBatch.call_count == 1
        batch_handler = given_stream_writer.foreachBatch.call_args.args[0]
        batch_handler(given_batch, 0)
        assert mock_append_batch.call_count == 1
        assert mock_append_batch.call_args.args == (given_batch, "raw/path")
        assert given_writer.option.call_count == 1
        assert given_writer.option.call_args.args == ("checkpointLocation", "checkpoint/path")
        assert given_writer.trigger.call_count == 1
        assert given_writer.start.call_count == 1
