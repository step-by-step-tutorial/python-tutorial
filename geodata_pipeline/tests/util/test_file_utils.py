from pathlib import Path

from geodata_pipeline.util.file_utils import read_tsv, resolve_path


def test_resolve_path_resolves_relative_path_against_base_dir(tmp_path: Path) -> None:
    assert resolve_path(tmp_path / "config", "../data/file.txt") == (tmp_path / "data" / "file.txt").resolve()


def test_resolve_path_keeps_absolute_path(tmp_path: Path) -> None:
    assert resolve_path(Path("/somewhere"), tmp_path) == tmp_path


def test_read_tsv_does_not_treat_quotes_as_field_delimiters(tmp_path: Path) -> None:
    path = tmp_path / "file.txt"
    path.write_text('1\t"Quoted\tvalue\n', encoding="utf-8")

    assert list(read_tsv(path)) == [["1", '"Quoted', "value"]]
