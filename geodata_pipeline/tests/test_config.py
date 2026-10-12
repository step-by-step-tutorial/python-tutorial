from pathlib import Path

from geodata_pipeline.config import PipelineConfig, Target


def make_target(**overrides) -> Target:
    values = {
        "country_code": "US",
        "country": "United States",
        "state_code": "CA",
        "state": "California",
        "cities": frozenset({"los angeles"}),
        "input_file": Path("in.parquet"),
        "output_file": Path("out.csv"),
    }
    return Target(**(values | overrides))


def test_from_file_resolves_paths_against_config_directory(project_dir: Path) -> None:
    config = PipelineConfig.from_file(project_dir / "config" / "targets.json")

    assert config.geonames_file == (project_dir / "data" / "allCountries.txt").resolve()
    assert config.output_dir == (project_dir / "output").resolve()
    assert config.targets[0].input_file == (project_dir / "data" / "addresses.parquet").resolve()
    assert config.targets[0].output_file == (project_dir / "output" / "los_angeles.csv").resolve()


def test_from_file_normalizes_city_names(project_dir: Path) -> None:
    config = PipelineConfig.from_file(project_dir / "config" / "targets.json")

    assert config.targets[0].cities == frozenset({"los angeles"})


def test_target_is_state_accepts_state_name_or_code() -> None:
    target = make_target()

    assert target.is_state("ca")
    assert target.is_state(" California ")
    assert not target.is_state("NV")


def test_target_is_city() -> None:
    target = make_target()

    assert target.is_city("Los  Angeles")
    assert not target.is_city(None)
    assert not target.is_city("San Diego")
