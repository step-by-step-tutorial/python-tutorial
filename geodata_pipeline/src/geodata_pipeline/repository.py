import csv
import logging
from collections.abc import Iterable
from pathlib import Path

from geodata_pipeline.config import Target
from geodata_pipeline.model import (
    GEONAMES_COLUMN_COUNT,
    POPULATED_PLACE_FEATURE_CLASS,
    POSTAL_CODES_MIN_COLUMN_COUNT,
    GeonameRecord,
    PostalCodeRecord,
)
from geodata_pipeline.text import normalize

logger = logging.getLogger(__name__)

StateKey = tuple[str, str]


class GeoDataRepository:
    """In-memory lookups of GeoNames places and postal codes for the states the targets cover."""

    def __init__(self, targets: Iterable[Target], geonames_file: Path, postal_codes_file: Path) -> None:
        self._states: set[StateKey] = {(target.country_code, target.state_code) for target in targets}
        self._geonames: dict[StateKey, dict[str, GeonameRecord]] = {state: {} for state in self._states}
        self._postal_codes: dict[StateKey, dict[str, PostalCodeRecord]] = {state: {} for state in self._states}
        self._load_geonames(geonames_file)
        self._load_postal_codes(postal_codes_file)

    def find_geoname(self, country_code: str, state_code: str, name: str) -> GeonameRecord | None:
        return self._geonames[(country_code, state_code)].get(normalize(name))

    def find_postal_code(self, country_code: str, state_code: str, postal_code: str) -> PostalCodeRecord | None:
        return self._postal_codes[(country_code, state_code)].get(postal_code)

    def _load_geonames(self, geonames_file: Path) -> None:
        loaded = 0
        logger.info("Loading GeoNames data from %s", geonames_file)

        for values in _read_tsv(geonames_file):
            if len(values) != GEONAMES_COLUMN_COUNT:
                continue

            record = GeonameRecord.from_values(values)

            # Only cities, towns and villages: other features (parks, buildings, counties) share city names.
            if record.feature_class != POPULATED_PLACE_FEATURE_CLASS:
                continue

            places = self._geonames.get((record.country_code, record.state_code))

            if places is None:
                continue

            for name in {normalize(record.name), normalize(record.ascii_name)}:
                current = places.get(name)
                # Several places can share a name; the most populated one is the city meant.
                if name and (current is None or record.population > current.population):
                    places[name] = record
            loaded += 1

        logger.info("Loaded %s GeoNames populated places for states=%s", loaded, sorted(self._states))

    def _load_postal_codes(self, postal_codes_file: Path) -> None:
        loaded = 0
        logger.info("Loading postal-code data from %s", postal_codes_file)

        for values in _read_tsv(postal_codes_file):
            if len(values) < POSTAL_CODES_MIN_COLUMN_COUNT:
                continue

            record = PostalCodeRecord.from_values(values)
            postal_codes = self._postal_codes.get((record.country_code, record.state_code))

            if postal_codes is None:
                continue

            postal_codes[record.postal_code] = record
            loaded += 1

        logger.info("Loaded %s postal-code records for states=%s", loaded, sorted(self._states))


def _read_tsv(path: Path) -> Iterable[list[str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        yield from csv.reader(file, delimiter="\t", quoting=csv.QUOTE_NONE)
