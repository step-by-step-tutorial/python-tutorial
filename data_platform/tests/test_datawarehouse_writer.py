import pandas as pd
import pytest

from dataset.definition import DataWarehouseEndpoint
from persistence.datawarehouse import writer as system_under_test

pytestmark = [pytest.mark.unit, pytest.mark.datawarehouse]


class TestWriteSpark:

    def test_should_write_partition_rows_in_chunks_and_close_client(self, mocker) -> None:
        given_client = mocker.Mock()
        mocker.patch.object(system_under_test.datawarehouse_connection_factory, "create_connection", return_value=given_client)

        class _Row:
            def __init__(self, value: int) -> None:
                self.value = value

            def asDict(self, recursive: bool = True):
                return {"value": self.value}

        class _Frame:
            columns = ["value"]

            def foreachPartition(self, callback):
                callback(iter(_Row(i) for i in range(1001)))

        system_under_test.write_spark(DataWarehouseEndpoint(full_table_name="db.table"), _Frame())

        assert given_client.insert_df.call_count == 2
        assert given_client.close.call_count == 2

    def test_should_write_pandas_dataframe_through_clickhouse_client(self, mocker) -> None:
        given_client = mocker.Mock()
        mocker.patch.object(system_under_test.datawarehouse_connection_factory, "create_connection", return_value=given_client)
        dataframe = pd.DataFrame({"value": [1]})

        system_under_test.write_pandas(DataWarehouseEndpoint(full_table_name="db.table"), dataframe)

        assert given_client.insert_df.call_count == 1
        assert given_client.close.call_count == 1
