import pandas as pd
import pytest

from dataset.definition import DataWarehouseEndpoint
from persistence.datawarehouse import datawarehouse_service as system_under_test

pytestmark = [pytest.mark.unit, pytest.mark.datawarehouse]


class TestTruncateAndPopulateFromPandas:

    def test_should_execute_preparing_sql_and_insert_dataframe(self, mocker) -> None:
        given_datawarehouse = DataWarehouseEndpoint(
            full_table_name="warehouse.example",
            before_setup_sql_files={"truncate": "truncate.sql"},
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

        actual = system_under_test.truncate_and_populate_from_memory(given_datawarehouse, given_dataframe)

        assert actual is None
        assert mock_create_connection.call_count == 1
        assert mock_read_text_file.call_count == 1
        assert given_connection.command.call_count == 1
        assert given_connection.insert_df.call_count == 1


class TestTruncateAndPopulateFromSpark:

    def test_should_execute_preparing_sql_and_insert_rows(self, mocker) -> None:
        given_datawarehouse = DataWarehouseEndpoint(
            full_table_name="warehouse.example",
            before_setup_sql_files={"truncate": "truncate.sql"},
        )
        given_dataframe = mocker.Mock()
        given_dataframe.columns = ["value"]

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
        mock_collect_rows = mocker.patch(
            "persistence.datawarehouse.datawarehouse_service.collect_rows",
            return_value=[(1,), (2,)],
        )
        mock_batch_rows = mocker.patch(
            "persistence.datawarehouse.datawarehouse_service.batch_rows",
            return_value=[[(1,)], [(2,)]],
        )

        actual = system_under_test.truncate_and_populate_from_spark(given_datawarehouse, given_dataframe)

        assert actual is None
        assert mock_create_connection.call_count == 1
        assert mock_read_text_file.call_count == 1
        assert given_connection.command.call_count == 1
        assert mock_collect_rows.call_count == 1
        assert mock_batch_rows.call_count == 1
        assert given_connection.insert.call_count == 2
        assert mock_batch_rows.call_args.args[0] == [(1,), (2,)]
        assert given_connection.insert.call_args_list[0].kwargs["table"] == "warehouse.example"
        assert given_connection.insert.call_args_list[0].kwargs["column_names"] == list(given_dataframe.columns)
        assert given_connection.insert.call_args_list[0].kwargs["data"] == [(1,)]
        assert given_connection.insert.call_args_list[1].kwargs["data"] == [(2,)]


class TestAnalyze:

    def test_should_execute_analysis_queries(self, mocker) -> None:
        given_datawarehouse = DataWarehouseEndpoint(
            after_setup_sql_files={"revenue": "select 1"},
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

        actual = system_under_test.analyze(given_datawarehouse)

        assert mock_create_connection.call_count == 1
        assert mock_read_text_file.call_count == 1
        assert given_connection.query_df.call_count == 1
        assert actual["revenue"] == given_connection.query_df.return_value
