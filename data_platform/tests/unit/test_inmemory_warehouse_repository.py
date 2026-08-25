import pandas as pd

from data_platform.model import WarehouseEndpoint
from data_platform.repository.inmemory_warehouse_repository import InmemoryWarehouseRepository


def build_endpoint() -> WarehouseEndpoint:
    return WarehouseEndpoint(
        connection_name="sale.warehouse",
        schema="warehouse",
        table_name="example",
        full_table_name="warehouse.example",
        create_sql_files={},
        truncate_sql_files={"truncate": "truncate.sql"},
        write_sql_files={},
        query_sql_files={"revenue": "revenue.sql"},
    )


class TestPandasWarehouseRepository:
    def test_should_replace_dataframe(self, mocker) -> None:
        connection = mocker.Mock()
        get_item = mocker.patch(
            "data_platform.persistence.warehouse_repository.connection_registry.get_item",
            return_value=connection,
        )
        mocker.patch("data_platform.persistence.warehouse_repository.read_text_file", return_value="truncate table warehouse.example")

        InmemoryWarehouseRepository(build_endpoint()).overwrite(pd.DataFrame({"id": [1]}))

        get_item.assert_called_once_with("sale.warehouse")
        connection.command.assert_called_once()
        connection.insert_df.assert_called_once()


