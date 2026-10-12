import logging
from collections.abc import Collection
from typing import Any

from shapely import wkb
from shapely.errors import ShapelyError

from geodata_pipeline.text import normalize

logger = logging.getLogger(__name__)


def extract_address_level_values(row: dict[str, Any]) -> list[str]:
    levels = row.get("address_levels") or []
    return [level["value"] for level in levels if isinstance(level, dict) and level.get("value")]


def matches_state(row: dict[str, Any], state_name: str, state_code: str) -> bool:
    normalized_states = {normalize(state_name), normalize(state_code)}
    return any(normalize(value) in normalized_states for value in extract_address_level_values(row))


def is_target_city(city: str | None, target_cities: Collection[str]) -> bool:
    return bool(city) and normalize(city) in target_cities


def get_coordinates(row: dict[str, Any]) -> tuple[float | None, float | None]:
    """Return (latitude, longitude) from the row's WKB point geometry, or (None, None) if it cannot be read."""
    geometry = row.get("geometry")

    if geometry is None:
        return None, None

    try:
        point = wkb.loads(geometry)
    except (ShapelyError, TypeError, ValueError) as error:
        logger.debug("Failed to parse geometry: %s", error)
        return None, None

    return point.y, point.x
