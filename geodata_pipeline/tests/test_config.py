from pathlib import Path

from geodata_pipeline.config import load_config


def test_load_config_resolves_paths_against_config_directory(project_dir: Path) -> None:
    config = load_config(project_dir / "config" / "targets.json")

    assert config.geonames_file == (project_dir / "data" / "allCountries.txt").resolve()
    assert config.output_dir == (project_dir / "output").resolve()
    assert config.targets[0].input_file == (project_dir / "data" / "addresses.parquet").resolve()
    assert config.targets[0].output_file == (project_dir / "output" / "los_angeles.csv").resolve()


def test_load_config_normalizes_city_names(project_dir: Path) -> None:
    config = load_config(project_dir / "config" / "targets.json")

    assert config.targets[0].cities == frozenset({"los angeles"})
