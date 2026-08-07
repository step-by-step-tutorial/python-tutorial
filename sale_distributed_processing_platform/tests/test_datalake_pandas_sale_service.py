import pandas as pd
import pytest

from service.datalake import datalake_pandas_sale_service as system_under_test


def create_connection_context(mocker):
    given_client = mocker.Mock()
    given_connection_context = mocker.MagicMock()
    given_connection_context.__enter__.return_value = given_client
    mock_create_connection = mocker.patch.object(
        system_under_test.datalake_connection_factory,
        "create_connection",
        return_value=given_connection_context
    )

    return given_client, given_connection_context, mock_create_connection


class TestUploadParquet:

    def test_should_create_bucket_and_upload_dataframe_under_given_path(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        mock_get_bucket_names = mocker.patch.object(system_under_test.datalake_sale_service, "get_bucket_names", return_value=[])

        # When
        actual = system_under_test.upload_parquet(df=given_dataframe, bucket_name=given_bucket_name,
                                                  path=given_path)

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
        assert given_client.put_object.call_args.kwargs == {"Bucket": given_bucket_name,
                                                            "Key": given_uploaded_object_key,
                                                            "Body": given_parquet_buffer}
        assert given_connection_context.__exit__.call_count == 1

    def test_should_normalize_path_before_upload(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = "sale-datalake"
        given_path = "/dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04/"
        given_normalized_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_client, given_connection_context, mock_create_connection = create_connection_context(mocker)

        mock_get_bucket_names = mocker.patch.object(system_under_test.datalake_sale_service, "get_bucket_names",
                                                    return_value=[given_bucket_name])

        # When
        actual = system_under_test.upload_parquet(df=given_dataframe, bucket_name=given_bucket_name,
                                                  path=given_path)

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

        mock_get_bucket_names = mocker.patch.object(system_under_test.datalake_sale_service, "get_bucket_names",
                                                    return_value=[given_bucket_name])

        # When
        actual = system_under_test.upload_parquet(df=given_dataframe, bucket_name=given_bucket_name,
                                                  path=given_path)

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
            system_under_test.upload_parquet(df=given_dataframe, bucket_name=given_bucket_name, path=given_path)

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

        mock_get_bucket_names = mocker.patch.object(system_under_test.datalake_sale_service, "get_bucket_names",
                                                    return_value=[given_bucket_name])
        given_client.put_object.side_effect = RuntimeError(given_error_message)

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.upload_parquet(df=given_dataframe, bucket_name=given_bucket_name, path=given_path)

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

        mock_read_parquet = mocker.patch.object(system_under_test.pd, "read_parquet",
                                                side_effect=[given_first_dataframe, given_second_dataframe])
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
        assert given_client.list_objects_v2.call_args.kwargs == {"Bucket": given_bucket_name,
                                                                 "Prefix": given_normalized_path}
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

        mock_read_parquet = mocker.patch.object(system_under_test.pd, "read_parquet",
                                                side_effect=RuntimeError(given_error_message))
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
