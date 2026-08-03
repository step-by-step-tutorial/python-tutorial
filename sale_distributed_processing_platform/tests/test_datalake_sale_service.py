from io import BytesIO

import pandas as pd
import pytest

from service import datalake_sale_service as system_under_test


def create_connection_context(mocker):
    given_client = mocker.Mock()
    given_connection_context = mocker.MagicMock()
    given_connection_context.__enter__.return_value = given_client
    mock_create_connection = mocker.patch.object(system_under_test.datalake_connection_factory, "create_connection", return_value=given_connection_context)

    return given_client, given_connection_context, mock_create_connection


class TestOverwrite:

    def test_should_overwrite_dataframe_as_partitioned_parquet(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_writer = given_dataframe.write
        given_output_uri = "s3a://sale-datalake/output/123"

        given_writer.mode.return_value = given_writer
        given_writer.partitionBy.return_value = given_writer

        mock_build_output_uri = mocker.patch.object(system_under_test.ec, "build_sale_datalake_output_uri", return_value=given_output_uri)

        # When
        actual = system_under_test.overwrite(given_dataframe)

        # Then
        assert actual is None
        assert given_writer.mode.call_count == 1
        assert given_writer.partitionBy.call_count == 1
        assert given_writer.parquet.call_count == 1
        assert mock_build_output_uri.call_count == 1
        assert given_writer.mode.call_args.args == ("overwrite",)
        assert given_writer.partitionBy.call_args.args == ("year", "month", "country")
        assert given_writer.parquet.call_args.args == (given_output_uri,)


class TestGetBucketNames:

    def test_should_return_bucket_names(self, mocker) -> None:
        # Given
        given_client = mocker.Mock()
        given_client.list_buckets.return_value = {
            "Buckets": [
                {"Name": "sale-datalake"},
                {"Name": "archive-datalake"},
            ]
        }

        # When
        actual = system_under_test.get_bucket_names(given_client)

        # Then
        assert actual == ["sale-datalake", "archive-datalake"]
        assert given_client.list_buckets.call_count == 1

    def test_should_return_empty_list_when_buckets_are_missing(self, mocker) -> None:
        # Given
        given_client = mocker.Mock()
        given_client.list_buckets.return_value = {}

        # When
        actual = system_under_test.get_bucket_names(given_client)

        # Then
        assert actual == []
        assert given_client.list_buckets.call_count == 1


class TestBucketList:

    def test_should_return_bucket_names_using_connection(self, mocker) -> None:
        # Given
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)
        given_bucket_names = ["sale-datalake"]

        mock_get_bucket_names = mocker.patch.object(system_under_test, "get_bucket_names", return_value=given_bucket_names)

        # When
        actual = system_under_test.bucket_list()

        # Then
        assert actual == given_bucket_names
        assert mock_create_connection.call_count == 1
        assert given_connection_context.__enter__.call_count == 1
        assert given_connection_context.__exit__.call_count == 1
        assert mock_get_bucket_names.call_count == 1
        assert mock_get_bucket_names.call_args.args == (given_client,)


class TestBucketExists:

    def test_should_return_true_when_bucket_exists(self, mocker) -> None:
        # Given
        given_bucket_name = "sale-datalake"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        mock_get_bucket_names = mocker.patch.object(system_under_test, "get_bucket_names", return_value=["sale-datalake", "archive-datalake"])

        # When
        actual = system_under_test.bucket_exists(given_bucket_name)

        # Then
        assert actual is True
        assert mock_create_connection.call_count == 1
        assert given_connection_context.__enter__.call_count == 1
        assert given_connection_context.__exit__.call_count == 1
        assert mock_get_bucket_names.call_count == 1
        assert mock_get_bucket_names.call_args.args == (given_client,)

    def test_should_return_false_when_bucket_does_not_exist(self, mocker) -> None:
        # Given
        given_bucket_name = "missing-datalake"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        mock_get_bucket_names = mocker.patch.object(system_under_test, "get_bucket_names", return_value=["sale-datalake"])

        # When
        actual = system_under_test.bucket_exists(given_bucket_name)

        # Then
        assert actual is False
        assert mock_create_connection.call_count == 1
        assert given_connection_context.__enter__.call_count == 1
        assert given_connection_context.__exit__.call_count == 1
        assert mock_get_bucket_names.call_count == 1
        assert mock_get_bucket_names.call_args.args == (given_client,)


class TestCreateBucketIfNotExists:

    def test_should_create_bucket_when_bucket_does_not_exist(self, mocker) -> None:
        # Given
        given_bucket_name = "sale-datalake"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        mock_get_bucket_names = mocker.patch.object(system_under_test, "get_bucket_names", return_value=[])

        # When
        actual = system_under_test.create_bucket_if_not_exists(given_bucket_name)

        # Then
        assert actual is None
        assert mock_create_connection.call_count == 1
        assert given_connection_context.__enter__.call_count == 1
        assert given_connection_context.__exit__.call_count == 1
        assert mock_get_bucket_names.call_count == 1
        assert given_client.create_bucket.call_count == 1
        assert mock_get_bucket_names.call_args.args == (given_client,)
        assert given_client.create_bucket.call_args.kwargs == {"Bucket": given_bucket_name}

    def test_should_not_create_bucket_when_bucket_exists(self, mocker) -> None:
        # Given
        given_bucket_name = "sale-datalake"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        mock_get_bucket_names = mocker.patch.object(system_under_test, "get_bucket_names", return_value=[given_bucket_name])

        # When
        actual = system_under_test.create_bucket_if_not_exists(given_bucket_name)

        # Then
        assert actual is None
        assert mock_create_connection.call_count == 1
        assert given_connection_context.__enter__.call_count == 1
        assert given_connection_context.__exit__.call_count == 1
        assert mock_get_bucket_names.call_count == 1
        assert given_client.create_bucket.call_count == 0
        assert mock_get_bucket_names.call_args.args == (given_client,)


class TestUploadAsParquet:

    def test_should_create_bucket_and_upload_dataframe_as_parquet(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_object_key = "sale/year=2026/month=8/data.parquet"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        mock_get_bucket_names = mocker.patch.object(system_under_test, "get_bucket_names", return_value=[])

        # When
        actual = system_under_test.upload_as_parquet(given_dataframe, given_bucket_name, given_object_key)

        # Then
        given_parquet_buffer = given_dataframe.to_parquet.call_args.args[0]

        assert actual is None
        assert mock_create_connection.call_count == 1
        assert given_connection_context.__enter__.call_count == 1
        assert given_connection_context.__exit__.call_count == 1
        assert mock_get_bucket_names.call_count == 1
        assert given_client.create_bucket.call_count == 1
        assert given_dataframe.to_parquet.call_count == 1
        assert given_client.put_object.call_count == 1
        assert isinstance(given_parquet_buffer, BytesIO)
        assert mock_get_bucket_names.call_args.args == (given_client,)
        assert given_client.create_bucket.call_args.kwargs == {"Bucket": given_bucket_name}
        assert given_dataframe.to_parquet.call_args.args == (given_parquet_buffer,)
        assert given_dataframe.to_parquet.call_args.kwargs == {"index": False}
        assert given_client.put_object.call_args.kwargs == {"Bucket": given_bucket_name, "Key": given_object_key, "Body": given_parquet_buffer}

    def test_should_not_create_existing_bucket_before_upload(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_object_key = "sale/data.parquet"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        mock_get_bucket_names = mocker.patch.object(system_under_test, "get_bucket_names", return_value=[given_bucket_name])

        # When
        actual = system_under_test.upload_as_parquet(given_dataframe, given_bucket_name, given_object_key)

        # Then
        assert actual is None
        assert mock_create_connection.call_count == 1
        assert given_connection_context.__enter__.call_count == 1
        assert given_connection_context.__exit__.call_count == 1
        assert mock_get_bucket_names.call_count == 1
        assert given_client.create_bucket.call_count == 0
        assert given_dataframe.to_parquet.call_count == 1
        assert given_client.put_object.call_count == 1

    def test_should_close_connection_when_upload_fails(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_object_key = "sale/data.parquet"
        given_error_message = "Upload failed"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        mocker.patch.object(system_under_test, "get_bucket_names", return_value=[given_bucket_name])
        given_client.put_object.side_effect = RuntimeError(given_error_message)

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.upload_as_parquet(given_dataframe, given_bucket_name, given_object_key)

        # Then
        assert str(actual.value) == given_error_message
        assert mock_create_connection.call_count == 1
        assert given_connection_context.__enter__.call_count == 1
        assert given_connection_context.__exit__.call_count == 1
        assert given_client.put_object.call_count == 1


class TestReadParquet:

    def test_should_download_and_return_parquet_dataframe(self, mocker) -> None:
        # Given
        given_bucket_name = "sale-datalake"
        given_object_key = "sale/data.parquet"
        given_dataframe = pd.DataFrame({"order_id": [1, 2]})
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        mock_read_parquet = mocker.patch.object(system_under_test.pd, "read_parquet", return_value=given_dataframe)

        # When
        actual = system_under_test.read_parquet(given_bucket_name, given_object_key)

        # Then
        given_parquet_buffer = given_client.download_fileobj.call_args.args[2]

        assert actual is given_dataframe
        assert mock_create_connection.call_count == 1
        assert given_connection_context.__enter__.call_count == 1
        assert given_connection_context.__exit__.call_count == 1
        assert given_client.download_fileobj.call_count == 1
        assert mock_read_parquet.call_count == 1
        assert isinstance(given_parquet_buffer, BytesIO)
        assert given_client.download_fileobj.call_args.args == (given_bucket_name, given_object_key, given_parquet_buffer)
        assert mock_read_parquet.call_args.args == (given_parquet_buffer,)