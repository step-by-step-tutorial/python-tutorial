from pathlib import Path

from geodata_pipeline.config import PipelineConfig
from geodata_pipeline.repository import GeoDataRepository


def load(project_dir: Path) -> tuple[PipelineConfig, GeoDataRepository]:
    config = PipelineConfig.from_file(project_dir / "config" / "targets.json")
    return config, GeoDataRepository(config.targets, config.geonames_file, config.postal_codes_file)


def test_find_geoname_prefers_most_populated_place_and_ignores_other_features(project_dir: Path) -> None:
    config, repository = load(project_dir)

    geoname = repository.find_geoname(config.targets[0], "LOS ANGELES")

    assert geoname is not None
    assert geoname.geoname_id == "5368361"
    assert geoname.population == 3820914


def test_find_geoname_only_loads_target_states(project_dir: Path) -> None:
    config, repository = load(project_dir)

    assert repository.find_geoname(config.targets[1], "los angeles") is None


def test_find_postal_code(project_dir: Path) -> None:
    config, repository = load(project_dir)

    postal_code = repository.find_postal_code(config.targets[0], "90049")

    assert postal_code is not None
    assert postal_code.city == "Los Angeles"
