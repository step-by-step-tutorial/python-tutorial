import pytest

from transformation.conversion.event_mapper import get_event_mapper
from dataset.sale.columns import SALE_COLUMNS
from dataset.house.columns import house_columns

pytestmark = pytest.mark.unit


class TestEventMapper:

    def test_should_map_sale_rows_to_prepared_events(self) -> None:
        mapper = get_event_mapper("sale")

        actual = mapper.map(
            {
                SALE_COLUMNS.ORDER_ID: "1",
                SALE_COLUMNS.CUSTOMER_NAME: "Ali Ahmadi",
                SALE_COLUMNS.PRODUCT_NAME: "Laptop",
                SALE_COLUMNS.CATEGORY: "Electronics",
                SALE_COLUMNS.QUANTITY: "2",
                SALE_COLUMNS.UNIT_PRICE: "1000",
                SALE_COLUMNS.ORDER_DATE: "2026-01-10",
                SALE_COLUMNS.COUNTRY: "Iran",
            }
        )

        assert actual.key == "1"
        assert actual.payload[SALE_COLUMNS.ORDER_ID] == 1
        assert actual.payload[SALE_COLUMNS.CUSTOMER_NAME] == "Ali Ahmadi"

    def test_should_map_sale_rows_with_pandas_typed_values(self) -> None:
        mapper = get_event_mapper("sale")

        actual = mapper.map(
            {
                SALE_COLUMNS.ORDER_ID: 1,
                SALE_COLUMNS.CUSTOMER_NAME: "Ali Ahmadi",
                SALE_COLUMNS.PRODUCT_NAME: "Laptop",
                SALE_COLUMNS.CATEGORY: "Electronics",
                SALE_COLUMNS.QUANTITY: 2,
                SALE_COLUMNS.UNIT_PRICE: 1000,
                SALE_COLUMNS.ORDER_DATE: "2026-01-10",
                SALE_COLUMNS.COUNTRY: "Iran",
            }
        )

        assert actual.key == "1"
        assert actual.payload[SALE_COLUMNS.ORDER_ID] == 1
        assert actual.payload[SALE_COLUMNS.QUANTITY] == 2.0

    def test_should_map_house_rows_to_prepared_events(self) -> None:
        mapper = get_event_mapper("house")

        actual = mapper.map(
            {
                house_columns.area_raw: "100",
                house_columns.room_raw: "2",
                house_columns.parking_raw: True,
                house_columns.warehouse_raw: False,
                house_columns.elevator_raw: True,
                house_columns.address_raw: "Tehran",
                house_columns.price_raw: "1000",
                house_columns.price_usd_raw: "25",
            }
        )

        assert actual.key == "Tehran"
        assert actual.payload[house_columns.address_raw] == "Tehran"
        assert actual.payload[house_columns.price_raw] == 1000.0

    def test_should_map_house_rows_with_missing_address_to_optional_key(self) -> None:
        mapper = get_event_mapper("house")

        actual = mapper.map(
            {
                house_columns.area_raw: 100,
                house_columns.room_raw: 2,
                house_columns.parking_raw: True,
                house_columns.warehouse_raw: False,
                house_columns.elevator_raw: True,
                house_columns.address_raw: None,
                house_columns.price_raw: 1000,
                house_columns.price_usd_raw: 25,
            }
        )

        assert actual.key is None
        assert actual.payload[house_columns.address_raw] is None

    def test_should_map_house_rows_with_comma_formatted_numbers(self) -> None:
        mapper = get_event_mapper("house")

        actual = mapper.map(
            {
                house_columns.area_raw: " 3,310,000,000 ",
                house_columns.room_raw: "2",
                house_columns.parking_raw: True,
                house_columns.warehouse_raw: True,
                house_columns.elevator_raw: True,
                house_columns.address_raw: "Ostad Moein",
                house_columns.price_raw: "3310000000.0",
                house_columns.price_usd_raw: "110333.33",
            }
        )

        assert actual.payload[house_columns.area_raw] == 3310000000.0
        assert actual.payload[house_columns.price_raw] == 3310000000.0

    def test_should_raise_for_unknown_dataset(self) -> None:
        with pytest.raises(KeyError):
            get_event_mapper("missing")
