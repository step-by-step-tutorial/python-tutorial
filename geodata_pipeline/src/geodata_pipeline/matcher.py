from geodata_pipeline.config import Target
from geodata_pipeline.model import AddressRecord, GeonameRecord, OvertureAddress
from geodata_pipeline.repository import GeoDataRepository


class AddressMatcher:
    """Matches Overture addresses to a target and turns the matching ones into output records."""

    def __init__(self, repository: GeoDataRepository) -> None:
        self._repository = repository

    def match(self, address: OvertureAddress, target: Target) -> AddressRecord | None:
        """Return the output record of an address in the target's state and cities, otherwise None."""
        if address.country != target.country_code or not address.is_in_state(target):
            return None

        city = self.find_city(address, target)

        if not target.is_city(city):
            return None

        return AddressRecord.from_overture_address(address, target, city, self.find_geoname(city, target))

    def find_city(self, address: OvertureAddress, target: Target) -> str | None:
        """Pick the city from the postal city, then the postal-code lookup, then the most specific address level."""
        if address.postal_city:
            return address.postal_city

        if address.postcode:
            postal_code = self._repository.find_postal_code(target, address.postcode)

            if postal_code:
                return postal_code.city

        return address.address_levels[-1] if address.address_levels else None

    def find_geoname(self, city: str | None, target: Target) -> GeonameRecord | None:
        if not city:
            return None

        return self._repository.find_geoname(target, city)
