from collections.abc import Iterable, Mapping, Sequence

from sqlalchemy import Column, MetaData, String, Table, create_engine


class DatabaseRepository:
    def __init__(self, url: str) -> None:
        self._url = url

    def write_rows(self, table_name: str, headers: Sequence[str], rows: Iterable[Mapping[str, str]]) -> None:
        row_list = [dict(row) for row in rows]

        engine = create_engine(self._url)

        metadata = MetaData()
        columns = (Column(header, String(), nullable=True) for header in headers)

        table = Table(table_name, metadata, *columns)
        table.drop(engine, checkfirst=True)
        metadata.create_all(engine, tables=[table])

        with engine.begin() as connection:
            if row_list:
                connection.execute(table.insert(), row_list)
