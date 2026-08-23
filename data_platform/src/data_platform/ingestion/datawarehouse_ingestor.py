
import pandas as pd

from data_platform.connector.connection_registry import get_connection
from data_platform.model import DataWarehouseEndpoint
from data_platform.util.file_utils import read_text_file


class DataWarehouseIngestor:
    def __init__(self, endpoint: DataWarehouseEndpoint) -> None:
        self.endpoint = endpoint

    def ingest(self, table_name: str) -> pd.DataFrame:
        query_file = self.endpoint.query_sql_files["select_all"]
        query = read_text_file(query_file).format(table_name=table_name)

        connection = get_connection(self.endpoint.connection_name)
        return connection.query_df(query)
