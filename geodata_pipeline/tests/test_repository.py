from pathlib import Path

from geodata_pipeline.config import load_config
from geodata_pipeline.repository import GeoDataRepository


def create_repository(project_dir: Path) -> GeoDataRepository:
    config = load_config(project_dir / "config" / "targets.json")
    return GeoDataRepository(config.targets, config.geonames_file, config.postal_codes_file)


def test_find_geoname_prefers_most_populated_place_and_ignores_other_features(project_dir: Path) -> None:
    geoname = create_repository(project_dir).find_geoname("US", "CA", "LOS ANGELES")

    assert geoname is not None
    assert geoname.geoname_id == "5368361"
    assert geoname.population == 3820914


def test_find_geoname_only_loads_target_states(project_dir: Path) -> None:
    repository = create_repository(project_dir)

    assert repository.find_geoname("US", "NY", "los angeles") is None


def test_find_postal_code(project_dir: Path) -> None:
    postal_code = create_repository(project_dir).find_postal_code("US", "CA", "90049")

    assert postal_code is not None
    assert postal_code.city == "Los Angeles"
