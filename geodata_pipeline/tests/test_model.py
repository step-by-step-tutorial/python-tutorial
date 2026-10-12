from pathlib import Path

from shapely.geometry import Point

from geodata_pipeline.model import (
    AddressModel,
    GeonameModel,
    OvertureAddressModel,
    PipelineConfigModel,
    PostalCodeModel,
    TargetModel,
)


def make_target(**overrides) -> TargetModel:
    values = {
        "country_code": "US",
        "country": "United States",
        "state_code": "CA",
        "state": "California",
        "cities": frozenset({"los angeles"}),
        "input_file": Path("in.parquet"),
        "output_file": Path("out.csv"),
    }
    return TargetModel(**(values | overrides))


def test_from_file_resolves_paths_against_config_directory(project_dir: Path) -> None:
    config = PipelineConfigModel.from_file(project_dir / "config" / "targets.json")

    assert config.geonames_file == (project_dir / "data" / "allCountries.txt").resolve()
    assert config.output_dir == (project_dir / "output").resolve()
    assert config.targets[0].input_file == (project_dir / "data" / "addresses.parquet").resolve()
    assert config.targets[0].output_file == (project_dir / "output" / "los_angeles.csv").resolve()


def test_from_file_normalizes_city_names(project_dir: Path) -> None:
    config = PipelineConfigModel.from_file(project_dir / "config" / "targets.json")

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


def test_overture_address_from_row_reads_levels_and_coordinates() -> None:
    address = OvertureAddressModel.from_row({
        "id": "a1",
        "geometry": Point(-118.24, 34.05).wkb,
        "country": "US",
        "street": "Main Street",
        "address_levels": [{"value": "CA"}, {"value": None}, "bad", {"value": "Los Angeles"}],
    })

    assert address.overture_id == "a1"
    assert address.postcode == ""
    assert address.address_levels == ("CA", "Los Angeles")
    assert (address.latitude, address.longitude) == (34.05, -118.24)


def test_overture_address_is_in_target_country_and_state() -> None:
    target = make_target()

    assert OvertureAddressModel.from_row({"country": "US", "address_levels": [{"value": "CA"}]}).is_in(target)
    assert not OvertureAddressModel.from_row({"country": "MX", "address_levels": [{"value": "CA"}]}).is_in(target)
    assert not OvertureAddressModel.from_row({"country": "US", "address_levels": [{"value": "NV"}]}).is_in(target)
    assert not OvertureAddressModel.from_row({"country": "US"}).is_in(target)


def test_overture_address_most_specific_level() -> None:
    levels = [{"value": "CA"}, {"value": "Pasadena"}]

    assert OvertureAddressModel.from_row({"address_levels": levels}).most_specific_level == "Pasadena"
    assert OvertureAddressModel.from_row({}).most_specific_level is None


def test_overture_address_columns_in_keeps_known_columns_in_model_order() -> None:
    assert OvertureAddressModel.columns_in(["extra", "country", "id"]) == ["id", "country"]


def test_address_record_from_overture_address_without_geoname() -> None:
    address = OvertureAddressModel.from_row({"id": "a1", "postcode": "90049"})

    record = AddressModel.from_overture_address(address, make_target(), "Los Angeles", None)

    assert record.city == "Los Angeles"
    assert record.postal_code == "90049"
    assert record.geoname_id == ""
    assert record.population is None


def test_geoname_record_from_values() -> None:
    values = [""] * 19
    values[0], values[1], values[6], values[8], values[10], values[14] = "1", "Los Angeles", "P", "US", "CA", ""

    record = GeonameModel.from_values(values)

    assert record.population == 0
    assert record.is_populated_place
    assert record.state_key == ("US", "CA")


def test_geoname_and_postal_code_is_valid_row() -> None:
    assert GeonameModel.is_valid_row([""] * 19)
    assert not GeonameModel.is_valid_row([""] * 18)
    assert PostalCodeModel.is_valid_row([""] * 12)
    assert not PostalCodeModel.is_valid_row([""] * 10)


def test_missing_source_files(project_dir: Path) -> None:
    config = PipelineConfigModel.from_file(project_dir / "config" / "targets.json")
    assert config.missing_source_files() == []

    config.geonames_file.unlink()
    assert config.missing_source_files() == [config.geonames_file]
