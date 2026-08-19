
from dataset.definition import DatabaseEndpoint
from util.database_utils import execute_sql
from util.file_utils import read_text_file


class DatabaseIngestor:
    def __init__(self, endpoint: DatabaseEndpoint) -> None:
        self.endpoint = endpoint

    def ingest(self, table_name: str):
        query_file = self.endpoint.query_sql_files["select_all"]
        query = read_text_file(query_file).format(table_name=table_name)
        return execute_sql(self.endpoint.connection_name, query)
