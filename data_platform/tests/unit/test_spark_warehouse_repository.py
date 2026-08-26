from data_platform.model.endpoints import WarehouseEndpoint
from data_platform.repository.spark_warehouse_repository import SparkWarehouseRepository


def build_endpoint() -> WarehouseEndpoint:
    return WarehouseEndpoint(
        connection_name="house.warehouse",
        schema="warehouse",
        table_name="example",
        full_table_name="warehouse.example",
        create_sql_files={},
        truncate_sql_files={"truncate": "truncate.sql"},
        write_sql_files={},
    )


class TestSparkWarehouseRepository:
    def test_should_replace_dataframe(self, mocker) -> None:
        dataframe = mocker.Mock()
        dataframe.columns = ["value"]
        connection = mocker.Mock()
        get_item = mocker.patch(
            "data_platform.repository.spark_warehouse_repository.connection_registry.get_item",
            return_value=connection,
        )
        mocker.patch("data_platform.repository.spark_warehouse_repository.read_text_file", return_value="truncate table warehouse.example")
        mocker.patch(
            "data_platform.repository.spark_warehouse_repository.dataframe_to_list",
            return_value=[(1,), (2,)],
        )
        mocker.patch(
            "data_platform.repository.spark_warehouse_repository.to_batches",
            return_value=[[(1,)], [(2,)]],
        )

        SparkWarehouseRepository(build_endpoint()).overwrite(dataframe)

        assert get_item.call_count == 3
        get_item.assert_any_call("house.warehouse")
        connection.command.assert_called_once()
        assert connection.insert.call_count == 2
        assert connection.insert.call_args_list[0].kwargs == {
            "table": "warehouse.example", "data": [(1,)], "column_names": ["value"]
        }
