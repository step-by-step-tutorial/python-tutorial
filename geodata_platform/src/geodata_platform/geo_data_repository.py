import logging
from collections.abc import Iterable
from pathlib import Path

from geodata_platform.model import GeonameModel, PostalCodeModel, StateKey, TargetModel
from geodata_platform.util.file_utils import read_tsv
from geodata_platform.util.text_utils import normalize

logger = logging.getLogger(__name__)

PlacesByName = dict[str, GeonameModel]
PostalCodesByCode = dict[str, PostalCodeModel]


class GeoDataRepository:
    """In-memory lookups of GeoNames populated places and postal codes, per (country, state)."""

    def __init__(
            self,
            places: dict[StateKey, PlacesByName],
            postal_codes: dict[StateKey, PostalCodesByCode],
    ) -> None:
        self._places = places
        self._postal_codes = postal_codes

    @classmethod
    def from_files(cls, targets: Iterable[TargetModel], geonames_file: Path, postal_codes_file: Path) -> "GeoDataRepository":
        """Read the GeoNames dumps once, keeping only the states the targets cover."""
        states = {target.state_key for target in targets}
        return cls(
            places=cls._read_places(geonames_file, states),
            postal_codes=cls._read_postal_codes(postal_codes_file, states),
        )

    def find_geoname(self, target: TargetModel, name: str | None) -> GeonameModel | None:
        return self._places.get(target.state_key, {}).get(normalize(name))

    def find_postal_code(self, target: TargetModel, postal_code: str) -> PostalCodeModel | None:
        return self._postal_codes.get(target.state_key, {}).get(postal_code)

    @staticmethod
    def _read_places(geonames_file: Path, states: set[StateKey]) -> dict[StateKey, PlacesByName]:
        places: dict[StateKey, PlacesByName] = {state: {} for state in states}
        loaded = 0
        logger.info("Loading GeoNames data from %s", geonames_file)

        for values in read_tsv(geonames_file):
            if not GeonameModel.is_valid_row(values):
                continue

            record = GeonameModel.from_values(values)
            state_places = places.get(record.state_key)

            # Only cities, towns and villages: other features (parks, buildings, counties) share city names.
            if state_places is None or not record.is_populated_place:
                continue

            for name in {normalize(record.name), normalize(record.ascii_name)}:
                current = state_places.get(name)
                # Several places can share a name; the most populated one is the city meant.
                if name and (current is None or record.population > current.population):
                    state_places[name] = record
            loaded += 1

        logger.info("Loaded %s GeoNames populated places for states=%s", loaded, sorted(states))
        return places

    @staticmethod
    def _read_postal_codes(postal_codes_file: Path, states: set[StateKey]) -> dict[StateKey, PostalCodesByCode]:
        postal_codes: dict[StateKey, PostalCodesByCode] = {state: {} for state in states}
        loaded = 0
        logger.info("Loading postal-code data from %s", postal_codes_file)

        for values in read_tsv(postal_codes_file):
            if not PostalCodeModel.is_valid_row(values):
                continue

            record = PostalCodeModel.from_values(values)
            state_postal_codes = postal_codes.get(record.state_key)

            if state_postal_codes is None:
                continue

            state_postal_codes[record.postal_code] = record
            loaded += 1

        logger.info("Loaded %s postal-code records for states=%s", loaded, sorted(states))
        return postal_codes
