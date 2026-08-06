from service.datalake import datalake_sale_service as system_under_test


def create_connection_context(mocker):
    given_client = mocker.Mock()
    given_connection_context = mocker.MagicMock()
    given_connection_context.__enter__.return_value = given_client
    mock_create_connection = mocker.patch.object(system_under_test.datalake_connection_factory, "create_connection",
                                                 return_value=given_connection_context)

    return given_client, given_connection_context, mock_create_connection


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

        mock_get_bucket_names = mocker.patch.object(system_under_test, "get_bucket_names",
                                                    return_value=given_bucket_names)

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

        mock_get_bucket_names = mocker.patch.object(system_under_test, "get_bucket_names",
                                                    return_value=["sale-datalake", "archive-datalake"])

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

        mock_get_bucket_names = mocker.patch.object(system_under_test, "get_bucket_names",
                                                    return_value=["sale-datalake"])

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

        mock_get_bucket_names = mocker.patch.object(system_under_test, "get_bucket_names",
                                                    return_value=[given_bucket_name])

        # When
        actual = system_under_test.create_bucket_if_not_exists(given_bucket_name)

        # Then
        assert actual is None
        assert mock_create_connection.call_count == 1
        assert mock_get_bucket_names.call_count == 1
        assert mock_get_bucket_names.call_args.args == (given_client,)
        assert given_client.create_bucket.call_count == 0
        assert given_connection_context.__exit__.call_count == 1
