import pytest

from data_platform.registry.event_converter_registry import event_converter_registry
from data_platform.registry.bootstrap import initialize_registries
from data_platform.domain.sale.attribute import attribute
from data_platform.domain.house.attribute import attribute

initialize_registries()


class TestEventConverter:

    def test_should_map_sale_rows_to_prepared_events(self) -> None:
        mapper = event_converter_registry.get_item("sale")

        actual = mapper.map(
            {
                attribute.ORDER_ID: "1",
                attribute.CUSTOMER_NAME: "Alex Johnson",
                attribute.PRODUCT_NAME: "Laptop",
                attribute.CATEGORY: "Electronics",
                attribute.QUANTITY: "2",
                attribute.UNIT_PRICE: "1000",
                attribute.ORDER_DATE: "2026-01-10",
                attribute.COUNTRY: "USA",
            }
        )

        assert actual.key == "1"
        assert actual.payload[attribute.ORDER_ID] == 1
        assert actual.payload[attribute.CUSTOMER_NAME] == "Alex Johnson"

    def test_should_map_sale_rows_with_pandas_typed_values(self) -> None:
        mapper = event_converter_registry.get_item("sale")

        actual = mapper.map(
            {
                attribute.ORDER_ID: 1,
                attribute.CUSTOMER_NAME: "Alex Johnson",
                attribute.PRODUCT_NAME: "Laptop",
                attribute.CATEGORY: "Electronics",
                attribute.QUANTITY: 2,
                attribute.UNIT_PRICE: 1000,
                attribute.ORDER_DATE: "2026-01-10",
                attribute.COUNTRY: "USA",
            }
        )

        assert actual.key == "1"
        assert actual.payload[attribute.ORDER_ID] == 1
        assert actual.payload[attribute.QUANTITY] == 2.0

    def test_should_map_house_rows_to_prepared_events(self) -> None:
        mapper = event_converter_registry.get_item("house")

        actual = mapper.map(
            {
                attribute.area_raw: "100",
                attribute.room_raw: "2",
                attribute.parking_raw: True,
                attribute.warehouse_raw: False,
                attribute.elevator_raw: True,
                attribute.address_raw: "Austin",
                attribute.price_raw: "1000",
                attribute.price_usd_raw: "25",
            }
        )

        assert actual.key == "Austin"
        assert actual.payload[attribute.address_raw] == "Austin"
        assert actual.payload[attribute.price_raw] == 1000.0

    def test_should_map_house_rows_with_missing_address_to_optional_key(self) -> None:
        mapper = event_converter_registry.get_item("house")

        actual = mapper.map(
            {
                attribute.area_raw: 100,
                attribute.room_raw: 2,
                attribute.parking_raw: True,
                attribute.warehouse_raw: False,
                attribute.elevator_raw: True,
                attribute.address_raw: None,
                attribute.price_raw: 1000,
                attribute.price_usd_raw: 25,
            }
        )

        assert actual.key is None
        assert actual.payload[attribute.address_raw] is None

    def test_should_map_house_rows_with_comma_formatted_numbers(self) -> None:
        mapper = event_converter_registry.get_item("house")

        actual = mapper.map(
            {
                attribute.area_raw: " 3,310,000,000 ",
                attribute.room_raw: "2",
                attribute.parking_raw: True,
                attribute.warehouse_raw: True,
                attribute.elevator_raw: True,
                attribute.address_raw: "Maple Avenue",
                attribute.price_raw: "3310000000.0",
                attribute.price_usd_raw: "110333.33",
            }
        )

        assert actual.payload[attribute.area_raw] == 3310000000.0
        assert actual.payload[attribute.price_raw] == 3310000000.0

    def test_should_raise_for_unknown_dataset(self) -> None:
        with pytest.raises(ValueError):
            event_converter_registry.get_item("missing")


