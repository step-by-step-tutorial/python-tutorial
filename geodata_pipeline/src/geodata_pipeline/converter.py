from typing import Any

from geodata_pipeline.address import get_coordinates
from geodata_pipeline.config import Target
from geodata_pipeline.model import AddressRecord, GeonameRecord


def to_address_record(row: dict[str, Any], target: Target, city: str, geoname: GeonameRecord | None) -> AddressRecord:
    latitude, longitude = get_coordinates(row)

    return AddressRecord(
        country=target.country,
        country_code=target.country_code,
        state=target.state,
        state_code=target.state_code,
        city=city,
        postal_code=row.get("postcode") or "",
        street=row.get("street") or "",
        house_number=row.get("number") or "",
        unit=row.get("unit") or "",
        latitude=latitude,
        longitude=longitude,
        geoname_id=geoname.geoname_id if geoname else "",
        timezone=geoname.timezone if geoname else "",
        population=geoname.population if geoname else None,
        overture_id=row.get("id") or "",
    )
