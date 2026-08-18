import pandas as pd
import pytest

from dataset.definition import DataWarehouseEndpoint
from persistence import datawarehouse_repository as system_under_test

pytestmark = [pytest.mark.unit, pytest.mark.datawarehouse]


class TestTruncateAndPopulateFromPandas:

    def test_should_execute_preparing_sql_and_insert_dataframe(self, mocker) -> None:
        given_datawarehouse = DataWarehouseEndpoint(
            connection_name="sale.datawarehouse",
            schema="warehouse",
            table_name="example",
            full_table_name="warehouse.example",
            create_sql_files={"create": "create.sql"},
            truncate_sql_files={"truncate": "truncate.sql"},
            write_sql_files={},
        )
        given_dataframe = pd.DataFrame({"id": [1]})
        given_connection = mocker.Mock()
        mock_create_connection = mocker.patch(
            "persistence.datawarehouse_repository.get_connection",
            return_value=given_connection,
        )
        mock_read_text_file = mocker.patch(
            "persistence.datawarehouse_repository.read_text_file",
            return_value="truncate table warehouse.example",
        )

        repository = system_under_test.DataWarehouseRepository(given_datawarehouse)
        actual = repository.truncate_and_populate_from_memory(given_dataframe)

        assert actual is None
        assert mock_create_connection.call_count == 1
        assert mock_create_connection.call_args.args[0] == "sale.datawarehouse"
        assert mock_read_text_file.call_count == 1
        assert given_connection.command.call_count == 1
        assert given_connection.insert_df.call_count == 1
        assert given_datawarehouse.full_table_name == "warehouse.example"


class TestTruncateAndPopulateFromSpark:

    def test_should_execute_preparing_sql_and_insert_rows(self, mocker) -> None:
        given_datawarehouse = DataWarehouseEndpoint(
            connection_name="sale.datawarehouse",
            schema="warehouse",
            table_name="example",
            full_table_name="warehouse.example",
            create_sql_files={"create": "create.sql"},
            truncate_sql_files={"truncate": "truncate.sql"},
            write_sql_files={},
        )
        given_dataframe = mocker.Mock()
        given_dataframe.columns = ["value"]

        given_connection = mocker.Mock()
        mock_create_connection = mocker.patch(
            "persistence.datawarehouse_repository.get_connection",
            return_value=given_connection,
        )
        mock_read_text_file = mocker.patch(
            "persistence.datawarehouse_repository.read_text_file",
            return_value="truncate table warehouse.example",
        )
        repository = system_under_test.DataWarehouseRepository(given_datawarehouse)
        mock_collect_rows = mocker.patch(
            "persistence.datawarehouse_repository.dataframe_to_list",
            return_value=[(1,), (2,)],
        )
        mock_batch_rows = mocker.patch(
            "persistence.datawarehouse_repository.batch_of_list",
            return_value=[[(1,)], [(2,)]],
        )
        actual = repository.truncate_and_populate_from_spark(given_dataframe)

        assert actual is None
        assert mock_create_connection.call_count == 1
        assert mock_create_connection.call_args.args[0] == "sale.datawarehouse"
        assert mock_read_text_file.call_count == 1
        assert given_connection.command.call_count == 1
        assert mock_collect_rows.call_count == 1
        assert mock_batch_rows.call_count == 1
        assert mock_batch_rows.call_args.args[0] == [(1,), (2,)]
        assert given_datawarehouse.full_table_name == "warehouse.example"
        assert given_connection.insert.call_count == 2
        assert given_connection.insert.call_args_list[0].kwargs["table"] == "warehouse.example"
        assert given_connection.insert.call_args_list[0].kwargs["column_names"] == list(given_dataframe.columns)
        assert given_connection.insert.call_args_list[0].kwargs["data"] == [(1,)]
        assert given_connection.insert.call_args_list[1].kwargs["data"] == [(2,)]


class TestAnalyze:

    def test_should_execute_analysis_queries(self, mocker) -> None:
        given_datawarehouse = DataWarehouseEndpoint(
            connection_name="sale.datawarehouse",
            schema="warehouse",
            table_name="example",
            full_table_name="warehouse.example",
            create_sql_files={},
            query_sql_files={"revenue": "select 1"},
        )
        given_connection = mocker.Mock()
        mock_create_connection = mocker.patch(
            "persistence.datawarehouse_repository.get_connection",
            return_value=given_connection,
        )
        mock_read_text_file = mocker.patch(
            "persistence.datawarehouse_repository.read_text_file",
            return_value="select 1",
        )

        repository = system_under_test.DataWarehouseRepository(given_datawarehouse)
        actual = repository.analyze(["revenue"])

        assert mock_create_connection.call_count == 1
        assert mock_create_connection.call_args.args[0] == "sale.datawarehouse"
        assert mock_read_text_file.call_count == 1
        assert given_connection.query_df.call_count == 1
        assert actual["revenue"] == given_connection.query_df.return_value
        assert given_datawarehouse.full_table_name == "warehouse.example"
