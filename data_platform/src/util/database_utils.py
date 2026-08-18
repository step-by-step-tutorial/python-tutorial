from __future__ import annotations

import pandas as pd
from sqlalchemy import text

from connector.database_connection_factory import get_connection


def execute_sql(connection_name: str, *queries: str):
    with get_connection(connection_name).begin() as connection:
        result_dataframe = None
        for query in queries:
            result = connection.execute(text(query))
            if getattr(result, "returns_rows", False) is True:
                result_dataframe = pd.DataFrame(result.fetchall(), columns=result.keys())
        connection.commit()
        return result_dataframe
