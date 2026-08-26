import pytest

from data_platform.registry.bootstrap import initialize_registries
from data_platform.domain.house.event_converter import house_event_converter
from data_platform.domain.house.attribute import attribute as house_attribute

initialize_registries()


class TestEventConverter:

    def test_should_map_house_rows_to_prepared_events(self) -> None:
        mapper = house_event_converter

        actual = mapper.map(
            {
                house_attribute.property_id: "p-1",
                house_attribute.property_type: "apartment",
                house_attribute.city: "Austin",
                house_attribute.area_sqm: "100",
                house_attribute.total_price: "1000",
            }
        )

        assert actual.key == "p-1"
        assert actual.payload[house_attribute.property_type] == "apartment"
        assert actual.payload[house_attribute.total_price] == "1000"

    def test_should_map_house_rows_with_missing_address_to_optional_key(self) -> None:
        mapper = house_event_converter

        actual = mapper.map(
            {
                house_attribute.property_id: None,
                house_attribute.area_sqm: 100,
                house_attribute.total_price: 1000,
            }
        )

        assert actual.key is None
        assert actual.payload[house_attribute.property_id] is None

    def test_should_map_house_rows_with_comma_formatted_numbers(self) -> None:
        mapper = house_event_converter

        actual = mapper.map(
            {
                house_attribute.property_id: "p-2",
                house_attribute.area_sqm: " 3,310,000,000 ",
                house_attribute.total_price: "3310000000.0",
            }
        )

        assert actual.payload[house_attribute.area_sqm] == " 3,310,000,000 "
        assert actual.payload[house_attribute.total_price] == "3310000000.0"
