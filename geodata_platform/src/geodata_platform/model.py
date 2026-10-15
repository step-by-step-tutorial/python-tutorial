from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from geodata_platform.util.file_utils import read_json, resolve_path
from geodata_platform.util.geometry_utils import wkb_point_to_lat_lon
from geodata_platform.util.text_utils import normalize

StateKey = tuple[str, str]


@dataclass(frozen=True)
class TargetModel:
    country_code: str
    country: str
    state_code: str
    state: str
    cities: frozenset[str]
    input_file: Path
    output_file: Path

    @classmethod
    def from_dict(cls, raw: dict[str, Any], base_dir: Path, output_dir: Path) -> "TargetModel":
        return cls(
            country_code=raw["country_code"],
            country=raw["country"],
            state_code=raw["state_code"],
            state=raw["state"],
            cities=frozenset(normalize(city) for city in raw["cities"]),
            input_file=resolve_path(base_dir, raw["input_file"]),
            output_file=output_dir / raw["output_file"],
        )

    @property
    def state_key(self) -> StateKey:
        return self.country_code, self.state_code

    def is_state(self, value: str) -> bool:
        return normalize(value) in {normalize(self.state), normalize(self.state_code)}

    def is_city(self, city: str | None) -> bool:
        return bool(city) and normalize(city) in self.cities


@dataclass(frozen=True)
class PipelineConfigModel:
    geonames_file: Path
    postal_codes_file: Path
    output_dir: Path
    targets: tuple[TargetModel, ...]

    @classmethod
    def from_file(cls, config_file: Path) -> "PipelineConfigModel":
        """Load the config; relative paths are resolved against the config file's directory."""
        base_dir = config_file.resolve().parent
        raw = read_json(config_file)
        output_dir = resolve_path(base_dir, raw["output_dir"])

        return cls(
            geonames_file=resolve_path(base_dir, raw["geonames_file"]),
            postal_codes_file=resolve_path(base_dir, raw["postal_codes_file"]),
            output_dir=output_dir,
            targets=tuple(TargetModel.from_dict(item, base_dir, output_dir) for item in raw["targets"]),
        )

    def missing_source_files(self) -> list[Path]:
        return [path for path in (self.geonames_file, self.postal_codes_file) if not path.is_file()]


@dataclass(frozen=True)
class GeonameModel:
    """One row of the GeoNames allCountries dump, see https://download.geonames.org/export/dump/readme.txt"""
    COLUMN_COUNT: ClassVar[int] = 19
    POPULATED_PLACE_FEATURE_CLASS: ClassVar[str] = "P"

    geoname_id: str
    name: str
    ascii_name: str
    feature_class: str
    country_code: str
    state_code: str
    population: int
    timezone: str

    @classmethod
    def is_valid_row(cls, values: list[str]) -> bool:
        return len(values) == cls.COLUMN_COUNT

    @classmethod
    def from_values(cls, values: list[str]) -> "GeonameModel":
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
    def state_key(self) -> StateKey:
        return self.country_code, self.state_code

    @property
    def is_populated_place(self) -> bool:
        return self.feature_class == self.POPULATED_PLACE_FEATURE_CLASS


@dataclass(frozen=True)
class PostalCodeModel:
    """One row of the GeoNames postal-code dump."""
    MIN_COLUMN_COUNT: ClassVar[int] = 11

    country_code: str
    postal_code: str
    city: str
    state: str
    state_code: str
    latitude: str
    longitude: str

    @classmethod
    def is_valid_row(cls, values: list[str]) -> bool:
        return len(values) >= cls.MIN_COLUMN_COUNT

    @classmethod
    def from_values(cls, values: list[str]) -> "PostalCodeModel":
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
    def state_key(self) -> StateKey:
        return self.country_code, self.state_code


@dataclass(frozen=True)
class OvertureAddressModel:
    """One row of an Overture Maps address Parquet file."""
    # Only the columns the pipeline reads, so the rest of the file is never decoded.
    COLUMNS: ClassVar[tuple[str, ...]] = (
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
    def columns_in(cls, column_names: list[str]) -> list[str]:
        """Return the address columns a file actually has."""
        return [column for column in cls.COLUMNS if column in column_names]

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "OvertureAddressModel":
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

    @property
    def most_specific_level(self) -> str | None:
        return self.address_levels[-1] if self.address_levels else None

    def is_in(self, target: TargetModel) -> bool:
        """Whether the address is in the target's country and state."""
        return self.country == target.country_code and any(target.is_state(level) for level in self.address_levels)


@dataclass(frozen=True)
class AddressModel:
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
            cls, address: OvertureAddressModel, target: TargetModel, city: str, geoname: GeonameModel | None
    ) -> "AddressModel":
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
