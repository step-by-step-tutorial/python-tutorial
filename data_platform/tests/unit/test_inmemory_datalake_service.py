from data_platform.repository import inmemory_datalake_repository as system_under_test
from data_platform.model.endpoints import DataLakeEndpoint


def create_connection_context(mocker):
    given_client = mocker.Mock()
    mock_create_connection = mocker.patch(
        "data_platform.repository.inmemory_datalake_repository.connection_registry.get_item",
        return_value=given_client,
    )

    return given_client, mock_create_connection

class TestUploadParquet:

    def test_should_create_bucket_and_upload_dataframe_under_given_path(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_client, mock_create_connection = create_connection_context(mocker)
        repository = system_under_test.DataLakeRepository(
            DataLakeEndpoint(connection_name="sale.datalake", bucket_name="app_datalake")
        )
        given_client.put_object.return_value = None

        # When
        actual = repository.write(
            data=given_dataframe,
            path="raw",
        )

        # Then
        assert actual is not None
        assert given_dataframe.to_parquet.call_count == 1
        assert mock_create_connection.call_count == 1
        assert given_client.list_buckets.call_count == 0
        assert given_client.put_object.call_count == 1
