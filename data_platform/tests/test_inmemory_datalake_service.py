import pandas as pd
import pytest

from persistence.datalake import datalake_service as system_under_test


def create_connection_context(mocker):
    given_client = mocker.Mock()
    given_connection_context = mocker.MagicMock()
    given_connection_context.__enter__.return_value = given_client
    mock_create_connection = mocker.patch.object(
        system_under_test.datalake_connection_factory,
        "create_connection",
        return_value=given_connection_context,
    )

    return given_client, given_connection_context, mock_create_connection


class TestGetBucketNames:

    def test_should_return_bucket_names(self, mocker) -> None:
        # Given
        given_client = mocker.Mock()
        given_client.list_buckets.return_value = {"Buckets": [{"Name": "app_datalake"}]}

        # When
        actual = system_under_test.get_bucket_names(given_client)

        # Then
        assert actual == ["app_datalake"]
        assert given_client.list_buckets.call_count == 1


class TestUploadParquet:

    def test_should_create_bucket_and_upload_dataframe_under_given_path(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_client, _, mock_create_connection = create_connection_context(mocker)
        mock_get_bucket_names = mocker.patch(
            "persistence.datalake.datalake_service.get_bucket_names",
            return_value=[],
        )
        given_client.put_object.return_value = None

        # When
        actual = system_under_test.upload(df=given_dataframe, bucket_name="app_datalake", relative_path="raw")

        # Then
        assert actual is not None
        assert given_dataframe.to_parquet.call_count == 1
        assert mock_create_connection.call_count == 1
        assert mock_get_bucket_names.call_count == 1
        assert given_client.create_bucket.call_count == 1
        assert given_client.put_object.call_count == 1


class TestDownloadParquet:

    def test_should_download_and_combine_all_parquet_files_under_path(self, mocker) -> None:
        # Given
        given_client, _, mock_create_connection = create_connection_context(mocker)
        given_client.list_objects_v2.return_value = {
            "Contents": [{"Key": "raw/part-001.parquet"}, {"Key": "raw/_SUCCESS"}]
        }
        mocker.patch.object(system_under_test.pd, "read_parquet", return_value=pd.DataFrame({"id": [1]}))
        mock_concat = mocker.patch.object(system_under_test.pd, "concat", return_value=pd.DataFrame({"id": [1]}))

        # When
        actual = system_under_test.download(bucket_name="app_datalake", relative_path="raw")

        # Then
        assert actual is not None
        assert mock_create_connection.call_count == 1
        assert given_client.list_objects_v2.call_count == 1
        assert given_client.download_fileobj.call_count == 1
        assert mock_concat.call_count == 1

    def test_should_raise_error_when_no_objects_exist_under_path(self, mocker) -> None:
        # Given
        given_client, _, mock_create_connection = create_connection_context(mocker)
        given_client.list_objects_v2.return_value = {}

        # When / Then
        with pytest.raises(FileNotFoundError):
            system_under_test.download(bucket_name="app_datalake", relative_path="raw")

        assert mock_create_connection.call_count == 1
        assert given_client.list_objects_v2.call_count == 1
