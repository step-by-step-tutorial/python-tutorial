import pandas as pd
import pytest

from dataset.house.attribute import HOUSE_ATTRIBUTE
from dataset.sale.attribute import SALE_ATTRIBUTE
from processor.inmemory.house_processor import InmemoryHouseProcessor
from processor.inmemory.sale_processor import InmemorySaleProcessor


class TestInmemorySaleProcessor:

    def test_should_clean_and_enrich_sale_records(self) -> None:
        dataframe = pd.DataFrame(
            [
                {
                    SALE_ATTRIBUTE.order_id: "1",
                    SALE_ATTRIBUTE.customer_name: "Alice",
                    SALE_ATTRIBUTE.product_name: "Chair",
                    SALE_ATTRIBUTE.category: "Furniture",
                    SALE_ATTRIBUTE.quantity: "2",
                    SALE_ATTRIBUTE.unit_price: "10",
                    SALE_ATTRIBUTE.order_date: "2026-01-10",
                    SALE_ATTRIBUTE.country: "USA",
                },
                {
                    SALE_ATTRIBUTE.order_id: "1",
                    SALE_ATTRIBUTE.customer_name: "Alice",
                    SALE_ATTRIBUTE.product_name: "Chair",
                    SALE_ATTRIBUTE.category: "Furniture",
                    SALE_ATTRIBUTE.quantity: "2",
                    SALE_ATTRIBUTE.unit_price: "10",
                    SALE_ATTRIBUTE.order_date: "2026-01-10",
                    SALE_ATTRIBUTE.country: "USA",
                },
                {
                    SALE_ATTRIBUTE.order_id: "2",
                    SALE_ATTRIBUTE.customer_name: "Bob",
                    SALE_ATTRIBUTE.product_name: "Desk",
                    SALE_ATTRIBUTE.category: "Electronics",
                    SALE_ATTRIBUTE.quantity: "",
                    SALE_ATTRIBUTE.unit_price: "20",
                    SALE_ATTRIBUTE.order_date: "2026-01-11",
                    SALE_ATTRIBUTE.country: "Canada",
                },
                {
                    SALE_ATTRIBUTE.order_id: "3",
                    SALE_ATTRIBUTE.customer_name: "Carol",
                    SALE_ATTRIBUTE.product_name: "Lamp",
                    SALE_ATTRIBUTE.category: "Furniture",
                    SALE_ATTRIBUTE.quantity: "-1",
                    SALE_ATTRIBUTE.unit_price: "5",
                    SALE_ATTRIBUTE.order_date: "invalid",
                    SALE_ATTRIBUTE.country: "UK",
                },
            ]
        )

        processor = InmemorySaleProcessor()
        cleaned = processor.clean(dataframe)
        enriched = processor.enrich(cleaned)

        assert len(cleaned) == 2
        assert list(cleaned[SALE_ATTRIBUTE.order_id]) == [1, 2]
        assert list(enriched[SALE_ATTRIBUTE.total_price]) == [20.0, 20.0]
        assert list(enriched[SALE_ATTRIBUTE.year]) == [2026, 2026]


class TestInmemoryHouseProcessor:

    def test_should_clean_and_enrich_house_records(self) -> None:
        dataframe = pd.DataFrame(
            [
                {
                    HOUSE_ATTRIBUTE.area_raw: " 3,310,000,000 ",
                    HOUSE_ATTRIBUTE.room_raw: "2",
                    HOUSE_ATTRIBUTE.parking_raw: "true",
                    HOUSE_ATTRIBUTE.warehouse_raw: "false",
                    HOUSE_ATTRIBUTE.elevator_raw: "true",
                    HOUSE_ATTRIBUTE.address_raw: " Ostad Moein ",
                    HOUSE_ATTRIBUTE.price_raw: "3310000000.0",
                    HOUSE_ATTRIBUTE.price_usd_raw: "110333.33",
                },
                {
                    HOUSE_ATTRIBUTE.area_raw: " 3,310,000,000 ",
                    HOUSE_ATTRIBUTE.room_raw: "2",
                    HOUSE_ATTRIBUTE.parking_raw: "true",
                    HOUSE_ATTRIBUTE.warehouse_raw: "false",
                    HOUSE_ATTRIBUTE.elevator_raw: "true",
                    HOUSE_ATTRIBUTE.address_raw: " Ostad Moein ",
                    HOUSE_ATTRIBUTE.price_raw: "3310000000.0",
                    HOUSE_ATTRIBUTE.price_usd_raw: "110333.33",
                },
                {
                    HOUSE_ATTRIBUTE.area_raw: "100",
                    HOUSE_ATTRIBUTE.room_raw: "1",
                    HOUSE_ATTRIBUTE.parking_raw: "false",
                    HOUSE_ATTRIBUTE.warehouse_raw: "false",
                    HOUSE_ATTRIBUTE.elevator_raw: "false",
                    HOUSE_ATTRIBUTE.address_raw: " Noor ",
                    HOUSE_ATTRIBUTE.price_raw: "1000",
                    HOUSE_ATTRIBUTE.price_usd_raw: "",
                },
                {
                    HOUSE_ATTRIBUTE.area_raw: "0",
                    HOUSE_ATTRIBUTE.room_raw: "1",
                    HOUSE_ATTRIBUTE.parking_raw: "false",
                    HOUSE_ATTRIBUTE.warehouse_raw: "false",
                    HOUSE_ATTRIBUTE.elevator_raw: "false",
                    HOUSE_ATTRIBUTE.address_raw: "Invalid",
                    HOUSE_ATTRIBUTE.price_raw: "10",
                    HOUSE_ATTRIBUTE.price_usd_raw: "1",
                },
            ]
        )

        processor = InmemoryHouseProcessor()
        cleaned = processor.clean(dataframe)
        enriched = processor.enrich(cleaned)

        assert len(cleaned) == 2
        assert list(cleaned[HOUSE_ATTRIBUTE.address]) == ["Ostad Moein", "Noor"]
        assert HOUSE_ATTRIBUTE.listing_key in enriched.columns
        assert list(enriched[HOUSE_ATTRIBUTE.price_per_square_meter]) == [1.0, 10.0]
