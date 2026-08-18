from __future__ import annotations

import pandas as pd

from dataset.definition import DatabaseEndpoint
from util import database_utils


class DatabaseIngestor:
    def __init__(self, endpoint: DatabaseEndpoint) -> None:
        self.endpoint = endpoint

    def ingest(self) -> pd.DataFrame:
        return database_utils.execute_sql(
            self.endpoint.connection_name,
            f"select * from {self.endpoint.full_stage_table_name}"
        )
