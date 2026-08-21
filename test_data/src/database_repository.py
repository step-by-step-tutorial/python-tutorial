from collections.abc import Iterable, Mapping, Sequence

from sqlalchemy import Column, MetaData, String, Table, create_engine, func, select


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

    def read_page(  self,  table_name: str,   page: int, page_size: int) -> tuple[list[dict[str, str | None]], int]:
        engine = create_engine(self._url)
        table = Table(table_name, MetaData(), autoload_with=engine)

        with engine.connect() as connection:
            total = connection.scalar(select(func.count()).select_from(table))
            rows = connection.execute(
                select(table).limit(page_size).offset((page - 1) * page_size)
            ).mappings().all()

        return [dict(row) for row in rows], total or 0
