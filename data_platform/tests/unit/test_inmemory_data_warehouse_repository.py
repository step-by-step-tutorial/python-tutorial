import pandas as pd

from data_platform.model import DataWarehouseEndpoint
from data_platform.persistence.inmemory_data_warehouse_repository import InmemoryDataWarehouseRepository


def build_endpoint() -> DataWarehouseEndpoint:
    return DataWarehouseEndpoint(
        connection_name="sale.datawarehouse",
        schema="warehouse",
        table_name="example",
        full_table_name="warehouse.example",
        create_sql_files={},
        truncate_sql_files={"truncate": "truncate.sql"},
        write_sql_files={},
        query_sql_files={"revenue": "revenue.sql"},
    )


class TestInmemoryDataWarehouseRepository:
    def test_should_replace_dataframe(self, mocker) -> None:
        connection = mocker.Mock()
        get_item = mocker.patch(
            "data_platform.persistence.data_warehouse_repository.connection_registry.get_item",
            return_value=connection,
        )
        mocker.patch("data_platform.persistence.data_warehouse_repository.read_text_file", return_value="truncate table warehouse.example")

        InmemoryDataWarehouseRepository(build_endpoint()).replace(pd.DataFrame({"id": [1]}))

        get_item.assert_called_once_with("sale.datawarehouse")
        connection.command.assert_called_once()
        connection.insert_df.assert_called_once()

    def test_should_find_query_results(self, mocker) -> None:
        connection = mocker.Mock()
        mocker.patch(
            "data_platform.persistence.data_warehouse_repository.connection_registry.get_item",
            return_value=connection,
        )
        mocker.patch("data_platform.persistence.data_warehouse_repository.read_text_file", return_value="select 1")

        actual = InmemoryDataWarehouseRepository(build_endpoint()).find_by_queries(["revenue"])

        connection.query_df.assert_called_once_with("select 1")
        assert actual == {"revenue": connection.query_df.return_value}
