from pathlib import Path

from csv_utils import count_rows


def test_count_rows_counts_data_rows_only(tmp_path: Path) -> None:
    path = tmp_path / "sample.csv"
    path.write_text("name\nAlice\nBob\n", encoding="utf-8")

    assert count_rows(path) == 2


def test_count_rows_handles_header_only_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("name\n", encoding="utf-8")

    assert count_rows(path) == 0
