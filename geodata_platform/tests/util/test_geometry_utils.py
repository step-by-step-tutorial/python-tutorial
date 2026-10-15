from shapely.geometry import Point

from geodata_platform.util.geometry_utils import wkb_point_to_lat_lon


def test_wkb_point_to_lat_lon_returns_latitude_then_longitude() -> None:
    assert wkb_point_to_lat_lon(Point(-118.24, 34.05).wkb) == (34.05, -118.24)


def test_wkb_point_to_lat_lon_returns_none_for_missing_or_invalid_geometry() -> None:
    assert wkb_point_to_lat_lon(None) == (None, None)
    assert wkb_point_to_lat_lon(b"not-wkb") == (None, None)
