import pytest

from data_platform.registry.bootstrap import initialize_registries
from data_platform.domain.sale.event_converter import sale_event_converter
from data_platform.domain.house.event_converter import house_event_converter
from data_platform.domain.sale.attribute import attribute as sale_attribute
from data_platform.domain.house.attribute import attribute as house_attribute

initialize_registries()


class TestEventConverter:

    def test_should_map_sale_rows_to_prepared_events(self) -> None:
        mapper = sale_event_converter

        actual = mapper.map(
            {
                sale_attribute.ORDER_ID: "1",
                sale_attribute.CUSTOMER_NAME: "Alex Johnson",
                sale_attribute.PRODUCT_NAME: "Laptop",
                sale_attribute.CATEGORY: "Electronics",
                sale_attribute.QUANTITY: "2",
                sale_attribute.UNIT_PRICE: "1000",
                sale_attribute.ORDER_DATE: "2026-01-10",
                sale_attribute.COUNTRY: "USA",
            }
        )

        assert actual.key == "1"
        assert actual.payload[sale_attribute.ORDER_ID] == 1
        assert actual.payload[sale_attribute.CUSTOMER_NAME] == "Alex Johnson"

    def test_should_map_sale_rows_with_pandas_typed_values(self) -> None:
        mapper = sale_event_converter

        actual = mapper.map(
            {
                sale_attribute.ORDER_ID: 1,
                sale_attribute.CUSTOMER_NAME: "Alex Johnson",
                sale_attribute.PRODUCT_NAME: "Laptop",
                sale_attribute.CATEGORY: "Electronics",
                sale_attribute.QUANTITY: 2,
                sale_attribute.UNIT_PRICE: 1000,
                sale_attribute.ORDER_DATE: "2026-01-10",
                sale_attribute.COUNTRY: "USA",
            }
        )

        assert actual.key == "1"
        assert actual.payload[sale_attribute.ORDER_ID] == 1
        assert actual.payload[sale_attribute.QUANTITY] == 2.0

    def test_should_map_house_rows_to_prepared_events(self) -> None:
        mapper = house_event_converter

        actual = mapper.map(
            {
                house_attribute.area_raw: "100",
                house_attribute.room_raw: "2",
                house_attribute.parking_raw: True,
                house_attribute.warehouse_raw: False,
                house_attribute.elevator_raw: True,
                house_attribute.address_raw: "Austin",
                house_attribute.price_raw: "1000",
                house_attribute.price_usd_raw: "25",
            }
        )

        assert actual.key == "Austin"
        assert actual.payload[house_attribute.address_raw] == "Austin"
        assert actual.payload[house_attribute.price_raw] == 1000.0

    def test_should_map_house_rows_with_missing_address_to_optional_key(self) -> None:
        mapper = house_event_converter

        actual = mapper.map(
            {
                house_attribute.area_raw: 100,
                house_attribute.room_raw: 2,
                house_attribute.parking_raw: True,
                house_attribute.warehouse_raw: False,
                house_attribute.elevator_raw: True,
                house_attribute.address_raw: None,
                house_attribute.price_raw: 1000,
                house_attribute.price_usd_raw: 25,
            }
        )

        assert actual.key is None
        assert actual.payload[house_attribute.address_raw] is None

    def test_should_map_house_rows_with_comma_formatted_numbers(self) -> None:
        mapper = house_event_converter

        actual = mapper.map(
            {
                house_attribute.area_raw: " 3,310,000,000 ",
                house_attribute.room_raw: "2",
                house_attribute.parking_raw: True,
                house_attribute.warehouse_raw: True,
                house_attribute.elevator_raw: True,
                house_attribute.address_raw: "Maple Avenue",
                house_attribute.price_raw: "3310000000.0",
                house_attribute.price_usd_raw: "110333.33",
            }
        )

        assert actual.payload[house_attribute.area_raw] == 3310000000.0
        assert actual.payload[house_attribute.price_raw] == 3310000000.0

