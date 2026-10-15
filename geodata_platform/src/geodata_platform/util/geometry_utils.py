import logging

from shapely import wkb
from shapely.errors import ShapelyError

logger = logging.getLogger(__name__)


def wkb_point_to_lat_lon(geometry: bytes | None) -> tuple[float | None, float | None]:
    """Return (latitude, longitude) of a WKB point, or (None, None) if it is missing or cannot be read."""
    if geometry is None:
        return None, None

    try:
        point = wkb.loads(geometry)
    except (ShapelyError, TypeError, ValueError) as error:
        logger.debug("Failed to parse geometry: %s", error)
        return None, None

    return point.y, point.x
