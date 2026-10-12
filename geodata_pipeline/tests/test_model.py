from shapely.geometry import Point

from geodata_pipeline.model import AddressRecord, GeonameRecord, OvertureAddress
from tests.test_config import make_target


def test_overture_address_from_row_reads_levels_and_coordinates() -> None:
    address = OvertureAddress.from_row({
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


def test_overture_address_is_in_state() -> None:
    target = make_target()

    assert OvertureAddress.from_row({"address_levels": [{"value": "CA"}]}).is_in_state(target)
    assert not OvertureAddress.from_row({"address_levels": [{"value": "NV"}]}).is_in_state(target)
    assert not OvertureAddress.from_row({}).is_in_state(target)


def test_address_record_column_names_follow_field_order() -> None:
    assert AddressRecord.column_names()[:3] == ["country", "country_code", "state"]
    assert AddressRecord.column_names()[-1] == "overture_id"


def test_address_record_from_overture_address_without_geoname() -> None:
    address = OvertureAddress.from_row({"id": "a1", "postcode": "90049"})

    record = AddressRecord.from_overture_address(address, make_target(), "Los Angeles", None)

    assert record.city == "Los Angeles"
    assert record.postal_code == "90049"
    assert record.geoname_id == ""
    assert record.population is None


def test_geoname_record_from_values() -> None:
    values = [""] * 19
    values[0], values[1], values[6], values[8], values[10], values[14] = "1", "Los Angeles", "P", "US", "CA", ""

    record = GeonameRecord.from_values(values)

    assert record.population == 0
    assert record.is_populated_place
    assert record.state_key == ("US", "CA")
