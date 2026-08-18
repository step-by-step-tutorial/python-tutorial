from __future__ import annotations

import pandas as pd

from dataset.definition import DataWarehouseEndpoint


class DataWarehouseIngestor:
    def __init__(self, endpoint: DataWarehouseEndpoint) -> None:
        self.endpoint = endpoint

    def ingest(self) -> pd.DataFrame:
        from connector.datawarehouse_connection_factory import get_connection

        connection = get_connection(self.endpoint.connection_name)
        query = f"select * from {self.endpoint.full_table_name}"
        return connection.query_df(query)
