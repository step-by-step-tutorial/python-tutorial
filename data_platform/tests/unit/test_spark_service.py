from pyspark.sql import DataFrame, SparkSession

from data_platform.model.endpoints import DataLakeEndpoint
from data_platform.service import spark_data_lake_service as system_under_test


class TestAppendBatchToObjectStorage:

    def test_should_persist_batch_before_appending(self, mocker) -> None:
        given_session = mocker.MagicMock(spec=SparkSession)
        given_dataframe = mocker.MagicMock(spec=DataFrame)
        given_dataframe.isEmpty.return_value = False
        given_persisted = mocker.Mock()
        given_context = mocker.MagicMock()
        given_context.__enter__.return_value = given_persisted
        given_context.__exit__.return_value = None

        service = system_under_test.SparkDataLakeService(
            session=given_session,
            data_lake_endpoint=DataLakeEndpoint(bucket_name="bucket"),
        )
        mock_persisted_dataframes = mocker.patch(
            "data_platform.service.spark_data_lake_service.persisted_dataframes",
            return_value=given_context,
        )
        mock_append = mocker.patch.object(service, "save")

        service.write_batch(given_dataframe, "cleaned/path")

        assert mock_persisted_dataframes.call_count == 1
        assert given_dataframe.persist.call_count == 1
        assert given_persisted.append.call_count == 1
        assert given_persisted.append.call_args.args == (given_dataframe.persist.return_value,)
        assert mock_append.call_count == 1
        assert mock_append.call_args.kwargs["dataframe"] is given_dataframe.persist.return_value
        assert mock_append.call_args.kwargs["path"] == "cleaned/path"


