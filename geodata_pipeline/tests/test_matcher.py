from pathlib import Path

from geodata_pipeline.model import OvertureAddressModel, PipelineConfigModel
from geodata_pipeline.repository import GeoDataRepository
from geodata_pipeline.matcher import AddressMatcher


def load(project_dir: Path):
    config = PipelineConfigModel.from_file(project_dir / "config" / "targets.json")
    repository = GeoDataRepository.from_files(config.targets, config.geonames_file, config.postal_codes_file)
    return config.targets[0], AddressMatcher(repository)


def address(**row) -> OvertureAddressModel:
    return OvertureAddressModel.from_row({"country": "US", "address_levels": [{"value": "CA"}]} | row)


def test_find_city_prefers_postal_city_then_postal_code_then_last_level(project_dir: Path) -> None:
    target, matcher = load(project_dir)

    assert matcher.find_city(address(postal_city="Santa Monica", postcode="90049"), target) == "Santa Monica"
    assert matcher.find_city(address(postcode="90049"), target) == "Los Angeles"
    assert matcher.find_city(address(address_levels=[{"value": "CA"}, {"value": "Pasadena"}]), target) == "Pasadena"


def test_match_returns_record_with_geoname(project_dir: Path) -> None:
    target, matcher = load(project_dir)

    record = matcher.match(address(postal_city="Los Angeles"), target)

    assert record is not None
    assert record.geoname_id == "5368361"


def test_match_skips_addresses_outside_target(project_dir: Path) -> None:
    target, matcher = load(project_dir)

    assert matcher.match(address(postal_city="San Diego"), target) is None
    assert matcher.match(address(country="MX", postal_city="Los Angeles"), target) is None
    assert matcher.match(address(postal_city="Los Angeles", address_levels=[{"value": "NV"}]), target) is None
