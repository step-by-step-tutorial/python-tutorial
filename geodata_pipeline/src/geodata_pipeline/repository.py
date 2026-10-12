import logging
from collections.abc import Iterable
from pathlib import Path

from geodata_pipeline.config import Target
from geodata_pipeline.model import (
    GEONAMES_COLUMN_COUNT,
    POSTAL_CODES_MIN_COLUMN_COUNT,
    GeonameRecord,
    PostalCodeRecord,
)
from geodata_pipeline.util.file_utils import read_tsv
from geodata_pipeline.util.text_utils import normalize

logger = logging.getLogger(__name__)

StateKey = tuple[str, str]


class GeoDataRepository:
    """In-memory lookups of GeoNames places and postal codes for the states the targets cover."""

    def __init__(self, targets: Iterable[Target], geonames_file: Path, postal_codes_file: Path) -> None:
        self._states: set[StateKey] = {target.state_key for target in targets}
        self._geonames: dict[StateKey, dict[str, GeonameRecord]] = {state: {} for state in self._states}
        self._postal_codes: dict[StateKey, dict[str, PostalCodeRecord]] = {state: {} for state in self._states}
        self._load_geonames(geonames_file)
        self._load_postal_codes(postal_codes_file)

    def find_geoname(self, target: Target, name: str) -> GeonameRecord | None:
        return self._geonames[target.state_key].get(normalize(name))

    def find_postal_code(self, target: Target, postal_code: str) -> PostalCodeRecord | None:
        return self._postal_codes[target.state_key].get(postal_code)

    def _load_geonames(self, geonames_file: Path) -> None:
        loaded = 0
        logger.info("Loading GeoNames data from %s", geonames_file)

        for values in read_tsv(geonames_file):
            if len(values) != GEONAMES_COLUMN_COUNT:
                continue

            record = GeonameRecord.from_values(values)
            places = self._geonames.get(record.state_key)

            # Only cities, towns and villages: other features (parks, buildings, counties) share city names.
            if places is None or not record.is_populated_place:
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

        for values in read_tsv(postal_codes_file):
            if len(values) < POSTAL_CODES_MIN_COLUMN_COUNT:
                continue

            record = PostalCodeRecord.from_values(values)
            postal_codes = self._postal_codes.get(record.state_key)

            if postal_codes is None:
                continue

            postal_codes[record.postal_code] = record
            loaded += 1

        logger.info("Loaded %s postal-code records for states=%s", loaded, sorted(self._states))
