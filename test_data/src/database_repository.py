from collections.abc import Iterable, Mapping, Sequence

from sqlalchemy import Column, MetaData, String, Table, create_engine, delete


DEFAULT_DATABASE_URL = "postgresql+psycopg2://test_data:test_data@localhost:5434/test_data"


class DatabaseRepository:
    def __init__(self, database_url: str | None = None) -> None:
        if database_url is None:
            import os

            database_url = os.environ.get("TEST_DATA_DATABASE_URL", DEFAULT_DATABASE_URL)
        self._database_url = database_url

    def write_rows(self, table_name: str, headers: Sequence[str], rows: Iterable[Mapping[str, str]]) -> None:
        row_list = [dict(row) for row in rows]

        engine = create_engine(self._database_url)
        metadata = MetaData()
        table = Table(
            table_name,
            metadata,
            *(Column(header, String(), nullable=True) for header in headers),
        )
        metadata.create_all(engine, tables=[table])

        with engine.begin() as connection:
            connection.execute(delete(table))
            if row_list:
                connection.execute(table.insert(), row_list)
