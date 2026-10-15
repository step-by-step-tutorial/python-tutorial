from dataclasses import dataclass
from pathlib import Path

from geodata_platform.util.file_utils import read_tsv, resolve_path, write_csv


def test_resolve_path_resolves_relative_path_against_base_dir(tmp_path: Path) -> None:
    assert resolve_path(tmp_path / "config", "../data/file.txt") == (tmp_path / "data" / "file.txt").resolve()


def test_resolve_path_keeps_absolute_path(tmp_path: Path) -> None:
    assert resolve_path(Path("/somewhere"), tmp_path) == tmp_path


def test_read_tsv_does_not_treat_quotes_as_field_delimiters(tmp_path: Path) -> None:
    path = tmp_path / "file.txt"
    path.write_text('1\t"Quoted\tvalue\n', encoding="utf-8")

    assert list(read_tsv(path)) == [["1", '"Quoted', "value"]]


@dataclass
class Row:
    name: str
    count: int | None


def test_write_csv_uses_field_names_as_header(tmp_path: Path) -> None:
    path = tmp_path / "out.csv"

    write_csv(path, Row, [Row("a", 1), Row("b", None)])

    assert path.read_text(encoding="utf-8").splitlines() == ["name,count", "a,1", "b,"]
