import logging

import pandas as pd

from data_platform.model import DataWarehouseEndpoint
from data_platform.registry.connection_registry import connection_registry
from data_platform.util.file_utils import read_text_file

logger = logging.getLogger(__name__)


class DataWarehouseIngestor:
    def __init__(self, endpoint: DataWarehouseEndpoint) -> None:
        self._endpoint = endpoint

    def ingest(self, table_name: str) -> pd.DataFrame:
        logger.info("Ingesting data warehouse table %s through %s", table_name, self._endpoint.connection_name)
        query_file = self._endpoint.query_sql_files["select_all"]
        query = read_text_file(query_file).format(table_name=table_name)

        connection = connection_registry.get_item(self._endpoint.connection_name)
        return connection.query_df(query)
import logging
