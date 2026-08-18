from __future__ import annotations

import pandas as pd

from connector.database_connection_factory import get_connection


class AuditDatabaseIngestor:
    def __init__(self, table_name: str) -> None:
        self.table_name = table_name

    def ingest(self) -> pd.DataFrame:
        engine = get_connection("audit.database")
        with engine.connect() as connection:
            return pd.read_sql_query(f"select * from {self.table_name}", connection)
