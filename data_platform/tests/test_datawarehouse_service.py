import pandas as pd

from dataset.definition import DataWarehouse
from persistence.datawarehouse import datawarehouse_service as system_under_test


class TestTruncateAndPopulate:

    def test_should_execute_preparing_sql_and_insert_dataframe(self, mocker) -> None:
        # Given
        given_datawarehouse = DataWarehouse(
            full_table_name="warehouse.example",
            preparing_sql_files={"truncate": "truncate.sql"},
        )
        given_dataframe = pd.DataFrame({"id": [1]})
        given_connection = mocker.Mock()
        given_context = mocker.MagicMock()
        given_context.__enter__.return_value = given_connection
        mock_create_connection = mocker.patch.object(
            system_under_test.datawarehouse_connection_factory,
            "create_connection",
            return_value=given_context,
        )
        mock_read_text_file = mocker.patch(
            "persistence.datawarehouse.datawarehouse_service.read_text_file",
            return_value="truncate table warehouse.example",
        )

        # When
        system_under_test.truncate_and_populate(given_datawarehouse, given_dataframe)

        # Then
        assert mock_create_connection.call_count == 1
        assert mock_read_text_file.call_count == 1
        assert given_connection.command.call_count == 1
        assert given_connection.insert_df.call_count == 1


class TestAnalyze:

    def test_should_execute_analysis_queries(self, mocker) -> None:
        # Given
        given_datawarehouse = DataWarehouse(
            analysis_sql_files={"revenue": "select 1"},
        )
        given_connection = mocker.Mock()
        given_context = mocker.MagicMock()
        given_context.__enter__.return_value = given_connection
        mock_create_connection = mocker.patch.object(
            system_under_test.datawarehouse_connection_factory,
            "create_connection",
            return_value=given_context,
        )
        mock_read_text_file = mocker.patch(
            "persistence.datawarehouse.datawarehouse_service.read_text_file",
            return_value="select 1",
        )

        # When
        actual = system_under_test.analyze(given_datawarehouse)

        # Then
        assert mock_create_connection.call_count == 1
        assert mock_read_text_file.call_count == 1
        assert given_connection.query_df.call_count == 1
        assert actual["revenue"] == given_connection.query_df.return_value
