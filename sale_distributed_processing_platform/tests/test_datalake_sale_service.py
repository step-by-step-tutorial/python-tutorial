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

    def test_should_overwrite_dataframe_as_parquet_without_partition_columns(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_dataframe.columns = ["order_id", "order_date", "country"]
        given_writer = given_dataframe.write
        given_bucket_name = "sale-datalake"
        given_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"

        given_writer.mode.return_value = given_writer

        # When
        actual = system_under_test.overwrite(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual is None
        assert given_writer.mode.call_count == 1
        assert given_writer.mode.call_args.args == ("overwrite",)
        assert given_writer.parquet.call_count == 1
        assert given_writer.parquet.call_args.args == (f"s3a://{given_bucket_name}/{given_path}",)

    def test_should_raise_error_when_dataframe_is_none(self) -> None:
        # Given
        given_dataframe = None
        given_bucket_name = "sale-datalake"
        given_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_error_message = "Cannot overwrite data because the dataframe is None."

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.overwrite(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message


    def test_should_raise_error_when_bucket_name_is_empty(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = " "
        given_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_error_message = "Cannot overwrite data because the bucket name is empty."

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.overwrite(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert given_dataframe.write.mode.call_count == 0
        assert given_dataframe.write.parquet.call_count == 0

    def test_should_raise_error_when_path_is_none(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_path = None
        given_error_message = "Cannot overwrite data because the data lake path is empty."

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.overwrite(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert given_dataframe.write.mode.call_count == 0
        assert given_dataframe.write.partitionBy.call_count == 0
        assert given_dataframe.write.parquet.call_count == 0

    def test_should_raise_error_when_path_is_empty(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_path = " "
        given_error_message = "Cannot overwrite data because the data lake path is empty."

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.overwrite(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert given_dataframe.write.mode.call_count == 0
        assert given_dataframe.write.partitionBy.call_count == 0
        assert given_dataframe.write.parquet.call_count == 0

    def test_should_propagate_error_when_setting_write_mode_fails(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_dataframe.columns = ["order_id"]
        given_writer = given_dataframe.write
        given_bucket_name = "sale-datalake"
        given_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_error_message = "Cannot set write mode"

        given_writer.mode.side_effect = RuntimeError(given_error_message)

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.overwrite(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert given_writer.mode.call_count == 1
        assert given_writer.parquet.call_count == 0

    def test_should_propagate_error_when_parquet_writing_without_partitions_fails(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_dataframe.columns = ["order_id"]
        given_writer = given_dataframe.write
        given_bucket_name = "sale-datalake"
        given_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_error_message = "Parquet writing failed"

        given_writer.mode.return_value = given_writer
        given_writer.parquet.side_effect = RuntimeError(given_error_message)

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.overwrite(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert given_writer.mode.call_count == 1
        assert given_writer.parquet.call_count == 1
        assert given_writer.parquet.call_args.args == (f"s3a://{given_bucket_name}/{given_path}",)


class TestRead:

    def test_should_read_parquet_dataframe_from_given_uri(self, mocker) -> None:
        # Given
        given_session = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_dataframe = mocker.Mock()

        given_session.read.parquet.return_value = given_dataframe

        # When
        actual = system_under_test.read(session=given_session, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual is given_dataframe
        assert given_session.read.parquet.call_count == 1
        assert given_session.read.parquet.call_args.args == (f"s3a://{given_bucket_name}/{given_path}",)

    def test_should_raise_error_when_session_is_none(self) -> None:
        # Given
        given_session = None
        given_bucket_name = "sale-datalake"
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_error_message = "Cannot read data because the Spark session is None."

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.read(session=given_session, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message


    def test_should_raise_error_when_bucket_name_is_empty(self, mocker) -> None:
        # Given
        given_session = mocker.Mock()
        given_bucket_name = " "
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_error_message = "Cannot read data because the bucket name is empty."

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.read(session=given_session, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert given_session.read.parquet.call_count == 0

    def test_should_raise_error_when_path_is_none(self, mocker) -> None:
        # Given
        given_session = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_path = None
        given_error_message = "Cannot read data because the data lake path is empty."

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.read(session=given_session, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert given_session.read.parquet.call_count == 0

    def test_should_raise_error_when_path_is_empty(self, mocker) -> None:
        # Given
        given_session = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_path = " "
        given_error_message = "Cannot read data because the data lake path is empty."

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.read(session=given_session, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert given_session.read.parquet.call_count == 0

    def test_should_propagate_error_when_parquet_reading_fails(self, mocker) -> None:
        # Given
        given_session = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_error_message = "Parquet reading failed"

        given_session.read.parquet.side_effect = RuntimeError(given_error_message)

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.read(session=given_session, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert given_session.read.parquet.call_count == 1
        assert given_session.read.parquet.call_args.args == (f"s3a://{given_bucket_name}/{given_path}",)


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
        assert mock_get_bucket_names.call_count == 1
        assert mock_get_bucket_names.call_args.args == (given_client,)
        assert given_connection_context.__exit__.call_count == 1


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
        assert mock_get_bucket_names.call_count == 1
        assert mock_get_bucket_names.call_args.args == (given_client,)
        assert given_connection_context.__exit__.call_count == 1

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
        assert mock_get_bucket_names.call_count == 1
        assert mock_get_bucket_names.call_args.args == (given_client,)
        assert given_connection_context.__exit__.call_count == 1


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
        assert mock_get_bucket_names.call_count == 1
        assert mock_get_bucket_names.call_args.args == (given_client,)
        assert given_client.create_bucket.call_count == 1
        assert given_client.create_bucket.call_args.kwargs == {"Bucket": given_bucket_name}
        assert given_connection_context.__exit__.call_count == 1

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
        assert mock_get_bucket_names.call_count == 1
        assert mock_get_bucket_names.call_args.args == (given_client,)
        assert given_client.create_bucket.call_count == 0
        assert given_connection_context.__exit__.call_count == 1

class TestUploadParquet:

    def test_should_create_bucket_and_upload_dataframe_under_given_path(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        mock_get_bucket_names = mocker.patch.object(system_under_test, "get_bucket_names", return_value=[])

        # When
        actual = system_under_test.upload_parquet(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        given_parquet_buffer = given_client.put_object.call_args.kwargs["Body"]
        given_uploaded_object_key = given_client.put_object.call_args.kwargs["Key"]

        assert actual == given_uploaded_object_key
        assert given_uploaded_object_key.startswith(f"{given_path.strip('/')}/part-")
        assert given_uploaded_object_key.endswith(".parquet")
        assert given_dataframe.to_parquet.call_count == 1
        assert given_dataframe.to_parquet.call_args.args == (given_parquet_buffer,)
        assert given_dataframe.to_parquet.call_args.kwargs == {"index": False}
        assert mock_create_connection.call_count == 1
        assert mock_get_bucket_names.call_count == 1
        assert mock_get_bucket_names.call_args.args == (given_client,)
        assert given_client.create_bucket.call_count == 1
        assert given_client.create_bucket.call_args.kwargs == {"Bucket": given_bucket_name}
        assert given_client.put_object.call_count == 1
        assert given_client.put_object.call_args.kwargs == {"Bucket": given_bucket_name, "Key": given_uploaded_object_key, "Body": given_parquet_buffer}
        assert given_connection_context.__exit__.call_count == 1

    def test_should_normalize_path_before_upload(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_path = "/dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04/"
        given_normalized_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        mock_get_bucket_names = mocker.patch.object(system_under_test, "get_bucket_names", return_value=[given_bucket_name])

        # When
        actual = system_under_test.upload_parquet(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        given_uploaded_object_key = given_client.put_object.call_args.kwargs["Key"]

        assert actual == given_uploaded_object_key
        assert given_uploaded_object_key.startswith(f"{given_normalized_path}/part-")
        assert given_uploaded_object_key.endswith(".parquet")
        assert given_dataframe.to_parquet.call_count == 1
        assert mock_create_connection.call_count == 1
        assert mock_get_bucket_names.call_count == 1
        assert mock_get_bucket_names.call_args.args == (given_client,)
        assert given_client.create_bucket.call_count == 0
        assert given_client.put_object.call_count == 1
        assert given_connection_context.__exit__.call_count == 1

    def test_should_not_create_existing_bucket_before_upload(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        mock_get_bucket_names = mocker.patch.object(system_under_test, "get_bucket_names", return_value=[given_bucket_name])

        # When
        actual = system_under_test.upload_parquet(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        given_uploaded_object_key = given_client.put_object.call_args.kwargs["Key"]

        assert actual == given_uploaded_object_key
        assert given_uploaded_object_key.startswith(f"{given_path.strip('/')}/part-")
        assert given_uploaded_object_key.endswith(".parquet")
        assert given_dataframe.to_parquet.call_count == 1
        assert mock_create_connection.call_count == 1
        assert mock_get_bucket_names.call_count == 1
        assert mock_get_bucket_names.call_args.args == (given_client,)
        assert given_client.create_bucket.call_count == 0
        assert given_client.put_object.call_count == 1
        assert given_connection_context.__exit__.call_count == 1

    def test_should_propagate_error_when_dataframe_conversion_fails(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_error_message = "Parquet conversion failed"

        given_dataframe.to_parquet.side_effect = RuntimeError(given_error_message)
        mock_create_connection = mocker.patch.object(system_under_test.datalake_connection_factory, "create_connection")

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.upload_parquet(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert given_dataframe.to_parquet.call_count == 1
        assert mock_create_connection.call_count == 0

    def test_should_propagate_error_when_upload_fails(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_error_message = "Upload failed"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        mock_get_bucket_names = mocker.patch.object(system_under_test, "get_bucket_names", return_value=[given_bucket_name])
        given_client.put_object.side_effect = RuntimeError(given_error_message)

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.upload_parquet(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert given_dataframe.to_parquet.call_count == 1
        assert mock_create_connection.call_count == 1
        assert mock_get_bucket_names.call_count == 1
        assert mock_get_bucket_names.call_args.args == (given_client,)
        assert given_client.put_object.call_count == 1
        assert given_connection_context.__exit__.call_count == 1

class TestDownloadParquet:

    def test_should_download_and_combine_all_parquet_files_under_path(self, mocker) -> None:
        # Given
        given_bucket_name = "sale-datalake"
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_first_object_key = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04/part-001.parquet"
        given_second_object_key = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04/year=2026/month=08/part-002.parquet"
        given_first_dataframe = pd.DataFrame({"order_id": [1, 2]})
        given_second_dataframe = pd.DataFrame({"order_id": [3, 4]})
        given_expected_dataframe = pd.DataFrame({"order_id": [1, 2, 3, 4]})
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        given_client.list_objects_v2.return_value = {
            "Contents": [
                {"Key": given_first_object_key},
                {"Key": "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04/_SUCCESS"},
                {"Key": given_second_object_key},
            ]
        }

        mock_read_parquet = mocker.patch.object(system_under_test.pd, "read_parquet", side_effect=[given_first_dataframe, given_second_dataframe])
        mock_concat = mocker.patch.object(system_under_test.pd, "concat", return_value=given_expected_dataframe)

        # When
        actual = system_under_test.download_parquet(bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual is given_expected_dataframe
        assert mock_create_connection.call_count == 1
        assert given_client.list_objects_v2.call_count == 1
        assert given_client.list_objects_v2.call_args.kwargs == {"Bucket": given_bucket_name, "Prefix": given_path}
        assert given_client.download_fileobj.call_count == 2
        assert mock_read_parquet.call_count == 2
        assert mock_concat.call_count == 1
        assert mock_concat.call_args.args == ([given_first_dataframe, given_second_dataframe],)
        assert mock_concat.call_args.kwargs == {"ignore_index": True}
        assert given_connection_context.__exit__.call_count == 1

    def test_should_normalize_path_before_listing_objects(self, mocker) -> None:
        # Given
        given_bucket_name = "sale-datalake"
        given_path = "/dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04/"
        given_normalized_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_object_key = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04/part-001.parquet"
        given_dataframe = pd.DataFrame({"order_id": [1]})
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        given_client.list_objects_v2.return_value = {"Contents": [{"Key": given_object_key}]}

        mock_read_parquet = mocker.patch.object(system_under_test.pd, "read_parquet", return_value=given_dataframe)
        mock_concat = mocker.patch.object(system_under_test.pd, "concat", return_value=given_dataframe)

        # When
        actual = system_under_test.download_parquet(bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual is given_dataframe
        assert mock_create_connection.call_count == 1
        assert given_client.list_objects_v2.call_count == 1
        assert given_client.list_objects_v2.call_args.kwargs == {"Bucket": given_bucket_name, "Prefix": given_normalized_path}
        assert given_client.download_fileobj.call_count == 1
        assert mock_read_parquet.call_count == 1
        assert mock_concat.call_count == 1
        assert given_connection_context.__exit__.call_count == 1

    def test_should_ignore_non_parquet_objects(self, mocker) -> None:
        # Given
        given_bucket_name = "sale-datalake"
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_object_key = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04/part-001.parquet"
        given_dataframe = pd.DataFrame({"order_id": [1]})
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        given_client.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04/_SUCCESS"},
                {"Key": "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04/metadata.json"},
                {"Key": given_object_key},
            ]
        }

        mock_read_parquet = mocker.patch.object(system_under_test.pd, "read_parquet", return_value=given_dataframe)
        mock_concat = mocker.patch.object(system_under_test.pd, "concat", return_value=given_dataframe)

        # When
        actual = system_under_test.download_parquet(bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual is given_dataframe
        assert mock_create_connection.call_count == 1
        assert given_client.list_objects_v2.call_count == 1
        assert given_client.download_fileobj.call_count == 1
        assert mock_read_parquet.call_count == 1
        assert mock_concat.call_count == 1
        assert given_connection_context.__exit__.call_count == 1

    def test_should_raise_error_when_no_objects_exist_under_path(self, mocker) -> None:
        # Given
        given_bucket_name = "sale-datalake"
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_error_message = "No Parquet files found under path: dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        given_client.list_objects_v2.return_value = {}
        mock_read_parquet = mocker.patch.object(system_under_test.pd, "read_parquet")
        mock_concat = mocker.patch.object(system_under_test.pd, "concat")

        # When
        with pytest.raises(FileNotFoundError) as actual:
            system_under_test.download_parquet(bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert mock_create_connection.call_count == 1
        assert given_client.list_objects_v2.call_count == 1
        assert given_client.download_fileobj.call_count == 0
        assert mock_read_parquet.call_count == 0
        assert mock_concat.call_count == 0
        assert given_connection_context.__exit__.call_count == 1

    def test_should_raise_error_when_path_contains_no_parquet_files(self, mocker) -> None:
        # Given
        given_bucket_name = "sale-datalake"
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_error_message = "No Parquet files found under path: dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        given_client.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04/_SUCCESS"},
                {"Key": "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04/metadata.json"},
            ]
        }

        mock_read_parquet = mocker.patch.object(system_under_test.pd, "read_parquet")
        mock_concat = mocker.patch.object(system_under_test.pd, "concat")

        # When
        with pytest.raises(FileNotFoundError) as actual:
            system_under_test.download_parquet(bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert mock_create_connection.call_count == 1
        assert given_client.list_objects_v2.call_count == 1
        assert given_client.download_fileobj.call_count == 0
        assert mock_read_parquet.call_count == 0
        assert mock_concat.call_count == 0
        assert given_connection_context.__exit__.call_count == 1

    def test_should_propagate_error_when_object_listing_fails(self, mocker) -> None:
        # Given
        given_bucket_name = "sale-datalake"
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_error_message = "Object listing failed"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        given_client.list_objects_v2.side_effect = RuntimeError(given_error_message)
        mock_read_parquet = mocker.patch.object(system_under_test.pd, "read_parquet")
        mock_concat = mocker.patch.object(system_under_test.pd, "concat")

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.download_parquet(bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert mock_create_connection.call_count == 1
        assert given_client.list_objects_v2.call_count == 1
        assert given_client.download_fileobj.call_count == 0
        assert mock_read_parquet.call_count == 0
        assert mock_concat.call_count == 0
        assert given_connection_context.__exit__.call_count == 1

    def test_should_propagate_error_when_parquet_download_fails(self, mocker) -> None:
        # Given
        given_bucket_name = "sale-datalake"
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_object_key = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04/part-001.parquet"
        given_error_message = "Download failed"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        given_client.list_objects_v2.return_value = {"Contents": [{"Key": given_object_key}]}
        given_client.download_fileobj.side_effect = RuntimeError(given_error_message)
        mock_read_parquet = mocker.patch.object(system_under_test.pd, "read_parquet")
        mock_concat = mocker.patch.object(system_under_test.pd, "concat")

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.download_parquet(bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert mock_create_connection.call_count == 1
        assert given_client.list_objects_v2.call_count == 1
        assert given_client.download_fileobj.call_count == 1
        assert mock_read_parquet.call_count == 0
        assert mock_concat.call_count == 0
        assert given_connection_context.__exit__.call_count == 1

    def test_should_propagate_error_when_parquet_conversion_fails(self, mocker) -> None:
        # Given
        given_bucket_name = "sale-datalake"
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_object_key = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04/part-001.parquet"
        given_error_message = "Parquet conversion failed"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        given_client.list_objects_v2.return_value = {"Contents": [{"Key": given_object_key}]}

        mock_read_parquet = mocker.patch.object(system_under_test.pd, "read_parquet", side_effect=RuntimeError(given_error_message))
        mock_concat = mocker.patch.object(system_under_test.pd, "concat")

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.download_parquet(bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert mock_create_connection.call_count == 1
        assert given_client.list_objects_v2.call_count == 1
        assert given_client.download_fileobj.call_count == 1
        assert mock_read_parquet.call_count == 1
        assert mock_concat.call_count == 0
        assert given_connection_context.__exit__.call_count == 1

    def test_should_propagate_error_when_dataframe_combination_fails(self, mocker) -> None:
        # Given
        given_bucket_name = "sale-datalake"
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_object_key = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04/part-001.parquet"
        given_dataframe = pd.DataFrame({"order_id": [1]})
        given_error_message = "Dataframe combination failed"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        given_client.list_objects_v2.return_value = {"Contents": [{"Key": given_object_key}]}

        mock_read_parquet = mocker.patch.object(system_under_test.pd, "read_parquet", return_value=given_dataframe)
        mock_concat = mocker.patch.object(system_under_test.pd, "concat", side_effect=RuntimeError(given_error_message))

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.download_parquet(bucket_name=given_bucket_name, path=given_path)

        # Then
        assert str(actual.value) == given_error_message
        assert mock_create_connection.call_count == 1
        assert given_client.list_objects_v2.call_count == 1
        assert given_client.download_fileobj.call_count == 1
        assert mock_read_parquet.call_count == 1
        assert mock_concat.call_count == 1
        assert given_connection_context.__exit__.call_count == 1