from pathlib import Path

import pytest

from test_data.util.file_utils import check_file_exists, list_directory_names, list_file_names, read_lines


def test_list_file_and_directory_names(tmp_path: Path) -> None:
    (tmp_path / "b.txt").write_text("", encoding="utf-8")
    (tmp_path / "a.txt").write_text("", encoding="utf-8")
    (tmp_path / "folder").mkdir()

    assert list_file_names(tmp_path) == ["a.txt", "b.txt"]
    assert list_directory_names(tmp_path) == ["folder"]


def test_read_lines_strips_and_skips_blank_lines(tmp_path: Path) -> None:
    path = tmp_path / "names.txt"
    path.write_text(" John \n\n  \nJane\n", encoding="utf-8")

    assert read_lines(path) == ("John", "Jane")


def test_check_file_exists(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        check_file_exists(tmp_path / "missing.txt")
