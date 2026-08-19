from __future__ import annotations

import pandas as pd

from connector import registry
from dataset.definition import DatabaseEndpoint
from util.file_utils import read_text_file


class DatabaseIngestor:
    def __init__(self, endpoint: DatabaseEndpoint) -> None:
        self.endpoint = endpoint

    def ingest(self, table_name: str):
        query_file = self.endpoint.query_sql_files["select_all"]
        query = read_text_file(query_file).format(table_name=table_name)
        with registry.get_connection(self.endpoint.connection_name) as connection:
            return pd.read_sql(query, connection)
