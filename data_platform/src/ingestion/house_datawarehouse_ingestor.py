from __future__ import annotations

import pandas as pd

from connector.datawarehouse_connection_factory import get_connection


class HouseDataWarehouseIngestor:
    def __init__(self, full_table_name: str) -> None:
        self.full_table_name = full_table_name

    def ingest(self) -> pd.DataFrame:
        connection = get_connection("house.datawarehouse")
        query = f"select * from {self.full_table_name}"
        return connection.query_df(query)
