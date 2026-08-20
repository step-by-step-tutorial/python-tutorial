from pathlib import Path

from sqlalchemy import create_engine, text

from database_repository import DatabaseRepository


def test_write_rows_creates_table_and_inserts_rows(tmp_path: Path) -> None:
    database_path = tmp_path / "test_data.sqlite"
    repository = DatabaseRepository(url=f"sqlite+pysqlite:///{database_path}")

    repository.write_rows(
        table_name="sample_output",
        headers=["order_id", "customer_name"],
        rows=[
            {"order_id": "1", "customer_name": "Alice"},
            {"order_id": "2", "customer_name": "Bob"},
        ],
    )

    engine = create_engine(f"sqlite+pysqlite:///{database_path}")
    with engine.connect() as connection:
        rows = connection.execute(
            text("select order_id, customer_name from sample_output order by order_id")
        ).mappings().all()

    assert rows == [
        {"order_id": "1", "customer_name": "Alice"},
        {"order_id": "2", "customer_name": "Bob"},
    ]


def test_write_rows_truncates_existing_rows_before_insert(tmp_path: Path) -> None:
    database_path = tmp_path / "test_data.sqlite"
    repository = DatabaseRepository(url=f"sqlite+pysqlite:///{database_path}")

    repository.write_rows(
        table_name="sample_output",
        headers=["order_id", "customer_name"],
        rows=[{"order_id": "1", "customer_name": "Alice"}],
    )
    repository.write_rows(
        table_name="sample_output",
        headers=["order_id", "customer_name"],
        rows=[{"order_id": "2", "customer_name": "Bob"}],
    )

    engine = create_engine(f"sqlite+pysqlite:///{database_path}")
    with engine.connect() as connection:
        rows = connection.execute(
            text("select order_id, customer_name from sample_output order by order_id")
        ).mappings().all()

    assert rows == [{"order_id": "2", "customer_name": "Bob"}]


def test_write_rows_recreates_table_when_columns_change(tmp_path: Path) -> None:
    database_path = tmp_path / "test_data.sqlite"
    repository = DatabaseRepository(url=f"sqlite+pysqlite:///{database_path}")

    repository.write_rows(
        table_name="sample_output",
        headers=["order_id", "customer_name"],
        rows=[{"order_id": "1", "customer_name": "Alice"}],
    )
    repository.write_rows(
        table_name="sample_output",
        headers=["order_id", "customer_name", "subtotal"],
        rows=[{"order_id": "2", "customer_name": "Bob", "subtotal": "25.0"}],
    )

    engine = create_engine(f"sqlite+pysqlite:///{database_path}")
    with engine.connect() as connection:
        columns = [row[1] for row in connection.execute(text("pragma table_info(sample_output)")).all()]
        rows = connection.execute(
            text("select order_id, customer_name, subtotal from sample_output")
        ).mappings().all()

    assert columns == ["order_id", "customer_name", "subtotal"]
    assert rows == [{"order_id": "2", "customer_name": "Bob", "subtotal": "25.0"}]
