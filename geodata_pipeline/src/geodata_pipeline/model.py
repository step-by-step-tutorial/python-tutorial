from dataclasses import dataclass, fields
from typing import Any

from geodata_pipeline.config import Target
from geodata_pipeline.util.geometry_utils import wkb_point_to_lat_lon

# Column layout of the GeoNames dump files, see https://download.geonames.org/export/dump/readme.txt
GEONAMES_COLUMN_COUNT = 19
POSTAL_CODES_MIN_COLUMN_COUNT = 11

POPULATED_PLACE_FEATURE_CLASS = "P"

# Only the Overture address columns the pipeline reads, so the rest of the file is never decoded.
OVERTURE_ADDRESS_COLUMNS = (
    "id",
    "geometry",
    "country",
    "postcode",
    "street",
    "number",
    "unit",
    "postal_city",
    "address_levels",
)


@dataclass(frozen=True)
class GeonameRecord:
    geoname_id: str
    name: str
    ascii_name: str
    feature_class: str
    country_code: str
    state_code: str
    population: int
    timezone: str

    @classmethod
    def from_values(cls, values: list[str]) -> "GeonameRecord":
        return cls(
            geoname_id=values[0],
            name=values[1],
            ascii_name=values[2],
            feature_class=values[6],
            country_code=values[8],
            state_code=values[10],
            population=int(values[14] or 0),
            timezone=values[17],
        )

    @property
    def state_key(self) -> tuple[str, str]:
        return self.country_code, self.state_code

    @property
    def is_populated_place(self) -> bool:
        return self.feature_class == POPULATED_PLACE_FEATURE_CLASS


@dataclass(frozen=True)
class PostalCodeRecord:
    country_code: str
    postal_code: str
    city: str
    state: str
    state_code: str
    latitude: str
    longitude: str

    @classmethod
    def from_values(cls, values: list[str]) -> "PostalCodeRecord":
        return cls(
            country_code=values[0],
            postal_code=values[1],
            city=values[2],
            state=values[3],
            state_code=values[4],
            latitude=values[9],
            longitude=values[10],
        )

    @property
    def state_key(self) -> tuple[str, str]:
        return self.country_code, self.state_code


@dataclass(frozen=True)
class OvertureAddress:
    """One row of an Overture Maps address Parquet file."""
    overture_id: str
    country: str
    postcode: str
    street: str
    number: str
    unit: str
    postal_city: str
    address_levels: tuple[str, ...]
    latitude: float | None
    longitude: float | None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "OvertureAddress":
        latitude, longitude = wkb_point_to_lat_lon(row.get("geometry"))
        levels = row.get("address_levels") or []

        return cls(
            overture_id=row.get("id") or "",
            country=row.get("country") or "",
            postcode=row.get("postcode") or "",
            street=row.get("street") or "",
            number=row.get("number") or "",
            unit=row.get("unit") or "",
            postal_city=row.get("postal_city") or "",
            address_levels=tuple(level["value"] for level in levels if isinstance(level, dict) and level.get("value")),
            latitude=latitude,
            longitude=longitude,
        )

    def is_in_state(self, target: Target) -> bool:
        return any(target.is_state(level) for level in self.address_levels)


@dataclass(frozen=True)
class AddressRecord:
    """One row of the output CSV."""
    country: str
    country_code: str
    state: str
    state_code: str
    city: str
    postal_code: str
    street: str
    house_number: str
    unit: str
    latitude: float | None
    longitude: float | None
    geoname_id: str
    timezone: str
    population: int | None
    overture_id: str

    @classmethod
    def from_overture_address(
            cls, address: OvertureAddress, target: Target, city: str, geoname: GeonameRecord | None
    ) -> "AddressRecord":
        return cls(
            country=target.country,
            country_code=target.country_code,
            state=target.state,
            state_code=target.state_code,
            city=city,
            postal_code=address.postcode,
            street=address.street,
            house_number=address.number,
            unit=address.unit,
            latitude=address.latitude,
            longitude=address.longitude,
            geoname_id=geoname.geoname_id if geoname else "",
            timezone=geoname.timezone if geoname else "",
            population=geoname.population if geoname else None,
            overture_id=address.overture_id,
        )

    @classmethod
    def column_names(cls) -> list[str]:
        return [field.name for field in fields(cls)]
