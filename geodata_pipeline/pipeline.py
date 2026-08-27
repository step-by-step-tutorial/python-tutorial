import csv
import logging
import re
from collections.abc import Collection
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq
from shapely import wkb

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "output"
GEONAMES_FILE = DATA_DIR / "allCountries.txt"
POSTAL_CODES_FILE = DATA_DIR / "postalCodes_allCountries.txt"
valid_country_codes = {"US"}

geonames_columns = [
    "geonameid",
    "name",
    "asciiname",
    "alternatenames",
    "latitude",
    "longitude",
    "feature_class",
    "feature_code",
    "country_code",
    "cc2",
    "admin1_code",
    "admin2_code",
    "admin3_code",
    "admin4_code",
    "population",
    "elevation",
    "dem",
    "timezone",
    "modification_date",
]
output_columns = [
    "country",
    "country_code",
    "state",
    "state_code",
    "city",
    "postal_code",
    "street",
    "house_number",
    "unit",
    "latitude",
    "longitude",
    "geoname_id",
    "timezone",
    "population",
    "overture_id",
]


@dataclass(frozen=True)
class Target:
    state_code: str
    state: str
    cities: frozenset[str]
    input_file: Path
    output_file: Path


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
    population: str
    overture_id: str


@dataclass(frozen=True)
class PostalCodeRecord:
    country_code: str
    postal_code: str
    city: str
    state: str
    state_code: str
    latitude: str
    longitude: str


targets = [
    Target(
        state_code="CA",
        state="California",
        cities=frozenset({"los angeles"}),
        input_file=DATA_DIR / "overture_los_angeles_addresses.parquet",
        output_file=OUTPUT_DIR / "los_angeles.csv",
    ),
    Target(
        state_code="NY",
        state="New York",
        cities=frozenset({"new york", "brooklyn", "bronx", "queens", "staten island"}),
        input_file=DATA_DIR / "overture_nyc_addresses.parquet",
        output_file=OUTPUT_DIR / "new_york.csv",
    ),
]


class TextUtils:
    @staticmethod
    def normalize(value: str | None) -> str:
        if not value:
            return ""

        value = value.strip().lower()
        return re.sub(r"\s+", " ", value)


class GeometryUtils:
    @staticmethod
    def get_coordinates(row: dict[str, Any]) -> tuple[float | None, float | None]:
        geometry = row.get("geometry")

        if geometry is None:
            return None, None

        try:
            point = wkb.loads(geometry)
            return point.y, point.x
        except Exception:
            return None, None


class AddressUtils:
    @staticmethod
    def extract_address_level_values(row: dict[str, Any]) -> list[str]:
        levels = row.get("address_levels") or []
        values = []

        for level in levels:
            if not isinstance(level, dict):
                continue

            value = level.get("value")

            if value:
                values.append(value)

        return values

    @staticmethod
    def matches_state(row: dict[str, Any], state_name: str, state_code: str) -> bool:
        normalized_states = {
            TextUtils.normalize(state_name),
            TextUtils.normalize(state_code),
        }

        for value in AddressUtils.extract_address_level_values(row):
            if TextUtils.normalize(value) in normalized_states:
                return True

        return False

    @staticmethod
    def is_target_city(city: str | None, target_cities: Collection[str]) -> bool:
        if not city:
            return False

        return TextUtils.normalize(city) in target_cities


class RecordConverter:
    @staticmethod
    def convert_postal_code(values: list[str]) -> PostalCodeRecord:
        return PostalCodeRecord(
            country_code=values[0],
            postal_code=values[1],
            city=values[2],
            state=values[3],
            state_code=values[4],
            latitude=values[9],
            longitude=values[10],
        )

    @staticmethod
    def convert_address(row: dict[str, Any], target: Target, city: str, geoname: dict[str, str] | None) -> dict[str, Any]:
        latitude, longitude = GeometryUtils.get_coordinates(row)

        return asdict(AddressRecord(
            country="United States",
            country_code="US",
            state=target.state,
            state_code=target.state_code,
            city=city,
            postal_code=row.get("postcode") or "",
            street=row.get("street") or "",
            house_number=row.get("number") or "",
            unit=row.get("unit") or "",
            latitude=latitude,
            longitude=longitude,
            geoname_id=geoname["geonameid"] if geoname else "",
            timezone=geoname["timezone"] if geoname else "",
            population=geoname["population"] if geoname else "",
            overture_id=row.get("id") or "",
        ))


class GeoDataRepository:
    def __init__(self) -> None:
        self.targets = targets
        self.geonames: dict[str, dict[str, dict[str, str]]] = {
            target.state_code: {} for target in self.targets
        }
        self.postal_codes: dict[str, dict[str, dict[str, str]]] = {
            target.state_code: {} for target in self.targets
        }
        self.load_geonames()
        self.load_postal_codes()

    def load_geonames(self) -> None:
        loaded = 0
        logger.info("Loading GeoNames data from %s", GEONAMES_FILE)
        with GEONAMES_FILE.open("r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter="\t")

            for values in reader:
                if len(values) != len(geonames_columns):
                    continue

                country_code = values[8]
                state_code = values[10]

                if country_code not in valid_country_codes or state_code not in self.geonames:
                    continue

                row = dict(zip(geonames_columns, values))
                names = {
                    TextUtils.normalize(row["name"]),
                    TextUtils.normalize(row["asciiname"]),
                }

                for name in names:
                    if name:
                        self.geonames[state_code].setdefault(name, row)
                loaded += 1

        logger.info("Loaded %s GeoNames records for states=%s", loaded, sorted(self.geonames))

    def load_postal_codes(self) -> None:
        loaded = 0
        logger.info("Loading postal-code data from %s", POSTAL_CODES_FILE)
        with POSTAL_CODES_FILE.open("r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter="\t")

            for values in reader:
                if len(values) < 11:
                    continue

                postal_code = RecordConverter.convert_postal_code(values)

                if (postal_code.country_code not in valid_country_codes
                        or postal_code.state_code not in self.postal_codes):
                    continue

                self.postal_codes[postal_code.state_code][postal_code.postal_code] = asdict(postal_code)
                loaded += 1

        logger.info("Loaded %s postal-code records for states=%s", loaded, sorted(self.postal_codes))

class AddressResolver:
    def __init__(self, repository: GeoDataRepository) -> None:
        self.repository = repository

    def find_city(self, row: dict[str, Any], state_code: str) -> str | None:
        postal_city = row.get("postal_city")

        if postal_city:
            return postal_city

        postcode = row.get("postcode")

        if postcode:
            postal = self.repository.postal_codes[state_code].get(postcode)

            if postal:
                return postal["city"]

        levels = AddressUtils.extract_address_level_values(row)

        if levels:
            return levels[-1]

        return None

    def find_geoname(self, city: str | None, state_code: str) -> dict[str, str] | None:
        if not city:
            return None

        return self.repository.geonames[state_code].get(TextUtils.normalize(city))


class Pipeline:
    def __init__(self) -> None:
        self.targets = targets
        self.repository = GeoDataRepository()
        self.address_resolver = AddressResolver(self.repository)

    def process_city(self, target: Target) -> None:
        input_file = target.input_file
        output_file = target.output_file
        state = target.state
        state_code = target.state_code

        logger.info("Processing target state=%s input=%s output=%s", state_code, input_file, output_file)

        parquet_file = pq.ParquetFile(input_file)
        processed = 0
        written = 0

        with output_file.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=output_columns)
            writer.writeheader()

            for batch in parquet_file.iter_batches(batch_size=50_000):
                for row in batch.to_pylist():
                    processed += 1

                    if (row.get("country") or "") not in valid_country_codes:
                        continue

                    if not AddressUtils.matches_state(row, state, state_code):
                        continue

                    city = self.address_resolver.find_city(row, state_code)

                    if not AddressUtils.is_target_city(city, target.cities):
                        continue

                    geoname = self.address_resolver.find_geoname(city, state_code)
                    output_row = RecordConverter.convert_address(row, target, city, geoname)

                    writer.writerow(output_row)
                    written += 1

                    if written % 100_000 == 0:
                        logger.info(
                            "Target state=%s progress scanned=%s written=%s",
                            state_code,
                            processed,
                            written,
                        )

        logger.info(
            "Finished target state=%s scanned=%s written=%s output=%s",
            state_code,
            processed,
            written,
            output_file,
        )

    def run(self) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        for target in self.targets:
            if not target.input_file.is_file():
                logger.warning(
                    "Skipping target state=%s: input file does not exist: %s",
                    target.state_code,
                    target.input_file,
                )
                continue

            self.process_city(target)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger.info("Starting geospatial data pipeline")
    Pipeline().run()
    logger.info("Geospatial data pipeline completed")


if __name__ == "__main__":
    main()
