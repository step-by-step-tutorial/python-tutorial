from pathlib import Path

import pytest

from test_data.util.csv_utils import read_csv_mapping, read_csv_rows, write_csv


def test_write_and_read_csv_rows(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "out" / "rows.csv", ["id", "name"], [{"id": "1", "name": "John"}])

    assert list(read_csv_rows(path)) == [{"id": "1", "name": "John"}]


def test_read_csv_mapping(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "map.csv", ["product", "price"], [{"product": "Desk", "price": "300"}])

    assert read_csv_mapping(path, "product", "price") == {"Desk": "300"}

    with pytest.raises(KeyError):
        read_csv_mapping(path, "product", "missing")
