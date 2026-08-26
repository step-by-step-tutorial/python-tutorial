import logging

from data_platform.model.endpoints import DatabaseEndpoint
from data_platform.util.database_utils import execute_query_strings
from data_platform.util.file_utils import read_text_file

logger = logging.getLogger(__name__)


class DatabaseIngestor:
    def __init__(self, endpoint: DatabaseEndpoint) -> None:
        self._endpoint = endpoint

    def ingest(self, table_name: str):
        logger.info("Ingesting database table %s through %s", table_name, self._endpoint.connection_name)
        query_file = self._endpoint.query_sql_files["select_all"]
        query = read_text_file(query_file).format(table_name=table_name)
        return execute_query_strings(self._endpoint.connection_name, (query,))
