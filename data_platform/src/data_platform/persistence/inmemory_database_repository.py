import pandas

from data_platform.model import DatabaseEndpoint
from data_platform.persistence.database_repository import DatabaseRepository
from data_platform.registry.connection_registry import connection_registry
from data_platform.util.collection_utils import list_of_values


class InmemoryDatabaseRepository(DatabaseRepository):
    def __init__(self, endpoint: DatabaseEndpoint) -> None:
        super().__init__(endpoint)

    def save(self, dataframe: pandas.DataFrame) -> None:
        with connection_registry.get_item(self._connection_name).begin() as connection:
            dataframe.to_sql(
                name=self._endpoint.stage_table_name,
                con=connection,
                schema=self._endpoint.schema or None,
                if_exists="append",
                index=False,
            )

    def replace(self, dataframe: pandas.DataFrame) -> None:
        self.truncate_stage_table()
        self.save(dataframe)
        self.execute_files(list_of_values(self._endpoint.write_sql_files))
