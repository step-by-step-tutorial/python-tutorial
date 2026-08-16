import pytest

from transformation.conversion.event_mapper import get_event_mapper
from dataset.sale.attribute import SALE_ATTRIBUTE
from dataset.house.attribute import HOUSE_ATTRIBUTE

pytestmark = pytest.mark.unit


class TestEventMapper:

    def test_should_map_sale_rows_to_prepared_events(self) -> None:
        mapper = get_event_mapper("sale")

        actual = mapper.map(
            {
                SALE_ATTRIBUTE.ORDER_ID: "1",
                SALE_ATTRIBUTE.CUSTOMER_NAME: "Ali Ahmadi",
                SALE_ATTRIBUTE.PRODUCT_NAME: "Laptop",
                SALE_ATTRIBUTE.CATEGORY: "Electronics",
                SALE_ATTRIBUTE.QUANTITY: "2",
                SALE_ATTRIBUTE.UNIT_PRICE: "1000",
                SALE_ATTRIBUTE.ORDER_DATE: "2026-01-10",
                SALE_ATTRIBUTE.COUNTRY: "Iran",
            }
        )

        assert actual.key == "1"
        assert actual.payload[SALE_ATTRIBUTE.ORDER_ID] == 1
        assert actual.payload[SALE_ATTRIBUTE.CUSTOMER_NAME] == "Ali Ahmadi"

    def test_should_map_sale_rows_with_pandas_typed_values(self) -> None:
        mapper = get_event_mapper("sale")

        actual = mapper.map(
            {
                SALE_ATTRIBUTE.ORDER_ID: 1,
                SALE_ATTRIBUTE.CUSTOMER_NAME: "Ali Ahmadi",
                SALE_ATTRIBUTE.PRODUCT_NAME: "Laptop",
                SALE_ATTRIBUTE.CATEGORY: "Electronics",
                SALE_ATTRIBUTE.QUANTITY: 2,
                SALE_ATTRIBUTE.UNIT_PRICE: 1000,
                SALE_ATTRIBUTE.ORDER_DATE: "2026-01-10",
                SALE_ATTRIBUTE.COUNTRY: "Iran",
            }
        )

        assert actual.key == "1"
        assert actual.payload[SALE_ATTRIBUTE.ORDER_ID] == 1
        assert actual.payload[SALE_ATTRIBUTE.QUANTITY] == 2.0

    def test_should_map_house_rows_to_prepared_events(self) -> None:
        mapper = get_event_mapper("house")

        actual = mapper.map(
            {
                HOUSE_ATTRIBUTE.area_raw: "100",
                HOUSE_ATTRIBUTE.room_raw: "2",
                HOUSE_ATTRIBUTE.parking_raw: True,
                HOUSE_ATTRIBUTE.warehouse_raw: False,
                HOUSE_ATTRIBUTE.elevator_raw: True,
                HOUSE_ATTRIBUTE.address_raw: "Tehran",
                HOUSE_ATTRIBUTE.price_raw: "1000",
                HOUSE_ATTRIBUTE.price_usd_raw: "25",
            }
        )

        assert actual.key == "Tehran"
        assert actual.payload[HOUSE_ATTRIBUTE.address_raw] == "Tehran"
        assert actual.payload[HOUSE_ATTRIBUTE.price_raw] == 1000.0

    def test_should_map_house_rows_with_missing_address_to_optional_key(self) -> None:
        mapper = get_event_mapper("house")

        actual = mapper.map(
            {
                HOUSE_ATTRIBUTE.area_raw: 100,
                HOUSE_ATTRIBUTE.room_raw: 2,
                HOUSE_ATTRIBUTE.parking_raw: True,
                HOUSE_ATTRIBUTE.warehouse_raw: False,
                HOUSE_ATTRIBUTE.elevator_raw: True,
                HOUSE_ATTRIBUTE.address_raw: None,
                HOUSE_ATTRIBUTE.price_raw: 1000,
                HOUSE_ATTRIBUTE.price_usd_raw: 25,
            }
        )

        assert actual.key is None
        assert actual.payload[HOUSE_ATTRIBUTE.address_raw] is None

    def test_should_map_house_rows_with_comma_formatted_numbers(self) -> None:
        mapper = get_event_mapper("house")

        actual = mapper.map(
            {
                HOUSE_ATTRIBUTE.area_raw: " 3,310,000,000 ",
                HOUSE_ATTRIBUTE.room_raw: "2",
                HOUSE_ATTRIBUTE.parking_raw: True,
                HOUSE_ATTRIBUTE.warehouse_raw: True,
                HOUSE_ATTRIBUTE.elevator_raw: True,
                HOUSE_ATTRIBUTE.address_raw: "Ostad Moein",
                HOUSE_ATTRIBUTE.price_raw: "3310000000.0",
                HOUSE_ATTRIBUTE.price_usd_raw: "110333.33",
            }
        )

        assert actual.payload[HOUSE_ATTRIBUTE.area_raw] == 3310000000.0
        assert actual.payload[HOUSE_ATTRIBUTE.price_raw] == 3310000000.0

    def test_should_raise_for_unknown_dataset(self) -> None:
        with pytest.raises(KeyError):
            get_event_mapper("missing")
