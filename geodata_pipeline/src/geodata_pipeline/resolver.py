from typing import Any

from geodata_pipeline.address import extract_address_level_values
from geodata_pipeline.config import Target
from geodata_pipeline.model import GeonameRecord
from geodata_pipeline.repository import GeoDataRepository


class AddressResolver:
    def __init__(self, repository: GeoDataRepository) -> None:
        self._repository = repository

    def find_city(self, row: dict[str, Any], target: Target) -> str | None:
        """Pick the city from the postal city, then the postal-code lookup, then the most specific address level."""
        postal_city = row.get("postal_city")

        if postal_city:
            return postal_city

        postcode = row.get("postcode")

        if postcode:
            postal_code = self._repository.find_postal_code(target.country_code, target.state_code, postcode)

            if postal_code:
                return postal_code.city

        levels = extract_address_level_values(row)
        return levels[-1] if levels else None

    def find_geoname(self, city: str | None, target: Target) -> GeonameRecord | None:
        if not city:
            return None

        return self._repository.find_geoname(target.country_code, target.state_code, city)
