from shapely.geometry import Point

from geodata_pipeline.address import extract_address_level_values, get_coordinates, is_target_city, matches_state
from geodata_pipeline.text import normalize


def test_normalize_lowercases_and_collapses_whitespace() -> None:
    assert normalize("  Los   Angeles ") == "los angeles"
    assert normalize(None) == ""


def test_extract_address_level_values_skips_empty_and_invalid_levels() -> None:
    row = {"address_levels": [{"value": "CA"}, {"value": None}, "bad", {"value": "Los Angeles"}]}

    assert extract_address_level_values(row) == ["CA", "Los Angeles"]


def test_matches_state_accepts_state_name_or_code() -> None:
    assert matches_state({"address_levels": [{"value": "ca"}]}, "California", "CA")
    assert matches_state({"address_levels": [{"value": "California"}]}, "California", "CA")
    assert not matches_state({"address_levels": [{"value": "NV"}]}, "California", "CA")
    assert not matches_state({}, "California", "CA")


def test_is_target_city() -> None:
    assert is_target_city("Los  Angeles", {"los angeles"})
    assert not is_target_city(None, {"los angeles"})
    assert not is_target_city("San Diego", {"los angeles"})


def test_get_coordinates_returns_latitude_then_longitude() -> None:
    assert get_coordinates({"geometry": Point(-118.24, 34.05).wkb}) == (34.05, -118.24)


def test_get_coordinates_returns_none_for_missing_or_invalid_geometry() -> None:
    assert get_coordinates({}) == (None, None)
    assert get_coordinates({"geometry": b"not-wkb"}) == (None, None)
