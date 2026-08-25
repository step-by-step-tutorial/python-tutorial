import pandas

from data_platform.model import DatabaseEndpoint
from data_platform.util.collection_utils import list_of_values
from data_platform.util.database_utils import execute_files


class DatabaseRepository:
    def __init__(self, endpoint: DatabaseEndpoint) -> None:
        self._endpoint = endpoint
        self._connection_name = endpoint.connection_name

    def execute_files(self, file_names: list[str]) -> None:
        execute_files(self._connection_name, file_names)

    def truncate_stage_table(self) -> None:
        self.execute_files(list_of_values(self._endpoint.truncate_sql_files))

    def replace(self, dataframe: pandas.DataFrame) -> None:
        raise NotImplementedError
