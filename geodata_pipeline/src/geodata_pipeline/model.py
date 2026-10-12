from dataclasses import dataclass, fields

# Column layout of the GeoNames dump files, see https://download.geonames.org/export/dump/readme.txt
GEONAMES_COLUMN_COUNT = 19
POSTAL_CODES_MIN_COLUMN_COUNT = 11

POPULATED_PLACE_FEATURE_CLASS = "P"


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


@dataclass(frozen=True)
class AddressRecord:
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


ADDRESS_COLUMNS = [field.name for field in fields(AddressRecord)]
