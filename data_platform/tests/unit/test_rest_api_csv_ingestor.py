from data_platform.ingestion.rest_api_csv_ingestor import RestApiCsvIngestor
from data_platform.model import RestApiEndpoint


class TestRestApiCsvIngestor:
    def test_should_download_csv(self, mocker) -> None:
        response = mocker.MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b"order_id,total_amount\n1,12.50\n"
        rest_connection = mocker.Mock()
        rest_connection.open.return_value = response
        mocker.patch("data_platform.ingestion.rest_api_csv_ingestor.build_opener", return_value=rest_connection)

        actual = RestApiCsvIngestor(
            RestApiEndpoint(url="http://test-data:8080/datasets/online_shopping/download?format=csv")
        ).ingest()

        assert actual.to_dict("records") == [{"order_id": 1, "total_amount": 12.5}]
        rest_connection.open.assert_called_once()
        assert rest_connection.open.call_args.args[0].method == "GET"


