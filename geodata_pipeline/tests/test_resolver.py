from pathlib import Path

from geodata_pipeline.config import PipelineConfig
from geodata_pipeline.model import OvertureAddress
from geodata_pipeline.repository import GeoDataRepository
from geodata_pipeline.resolver import AddressResolver


def load(project_dir: Path):
    config = PipelineConfig.from_file(project_dir / "config" / "targets.json")
    repository = GeoDataRepository(config.targets, config.geonames_file, config.postal_codes_file)
    return config.targets[0], AddressResolver(repository)


def address(**row) -> OvertureAddress:
    return OvertureAddress.from_row({"country": "US", "address_levels": [{"value": "CA"}]} | row)


def test_find_city_prefers_postal_city_then_postal_code_then_last_level(project_dir: Path) -> None:
    target, resolver = load(project_dir)

    assert resolver.find_city(address(postal_city="Santa Monica", postcode="90049"), target) == "Santa Monica"
    assert resolver.find_city(address(postcode="90049"), target) == "Los Angeles"
    assert resolver.find_city(address(address_levels=[{"value": "CA"}, {"value": "Pasadena"}]), target) == "Pasadena"


def test_resolve_returns_record_with_geoname(project_dir: Path) -> None:
    target, resolver = load(project_dir)

    record = resolver.resolve(address(postal_city="Los Angeles"), target)

    assert record is not None
    assert record.geoname_id == "5368361"


def test_resolve_skips_addresses_outside_target(project_dir: Path) -> None:
    target, resolver = load(project_dir)

    assert resolver.resolve(address(postal_city="San Diego"), target) is None
    assert resolver.resolve(address(country="MX", postal_city="Los Angeles"), target) is None
    assert resolver.resolve(address(postal_city="Los Angeles", address_levels=[{"value": "NV"}]), target) is None
