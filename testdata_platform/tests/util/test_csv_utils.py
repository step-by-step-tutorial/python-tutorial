from pathlib import Path

import pytest

from testdata_platform.util.csv_utils import filter_rows, read_csv_mapping, read_csv_rows, rows_with_values, write_csv


def test_write_and_read_csv_rows(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "out" / "rows.csv", ["id", "name"], [{"id": "1", "name": "John"}])

    assert list(read_csv_rows(path)) == [{"id": "1", "name": "John"}]


def test_read_csv_mapping(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "map.csv", ["product", "price"], [{"product": "Desk", "price": "300"}])

    assert read_csv_mapping(path, "product", "price") == {"Desk": "300"}

    with pytest.raises(KeyError):
        read_csv_mapping(path, "product", "missing")


def test_filter_rows_and_rows_with_values() -> None:
    rows = [{"kind": "R", "name": "Sunset"}, {"kind": "P", "name": ""}, {"kind": "P", "name": "Pasadena"}]

    assert filter_rows(rows, "kind", ["P"]) == (rows[1], rows[2])
    assert rows_with_values(rows, ["name"]) == (rows[0], rows[2])
