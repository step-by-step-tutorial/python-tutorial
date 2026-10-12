from geodata_pipeline.model import AddressModel, OvertureAddressModel, TargetModel
from geodata_pipeline.geo_data_repository import GeoDataRepository


class AddressMatcher:
    """Matches Overture addresses to a target and turns the matching ones into output records."""

    def __init__(self, repository: GeoDataRepository) -> None:
        self._repository = repository

    def match(self, address: OvertureAddressModel, target: TargetModel) -> AddressModel | None:
        """Return the output record of an address in the target's state and cities, otherwise None."""
        if not address.is_in(target):
            return None

        city = self.find_city(address, target)

        if not target.is_city(city):
            return None

        return AddressModel.from_overture_address(address, target, city, self._repository.find_geoname(target, city))

    def find_city(self, address: OvertureAddressModel, target: TargetModel) -> str | None:
        """Pick the city from the postal city, then the postal-code lookup, then the most specific address level."""
        if address.postal_city:
            return address.postal_city

        if address.postcode:
            postal_code = self._repository.find_postal_code(target, address.postcode)

            if postal_code:
                return postal_code.city

        return address.most_specific_level

