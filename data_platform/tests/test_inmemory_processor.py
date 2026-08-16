from __future__ import annotations

import pandas as pd
import pytest

from dataset.house.columns import house_columns
from dataset.sale.columns import sale_columns
from processor.inmemory.house_processor import InmemoryHouseProcessor
from processor.inmemory.sale_processor import InmemorySaleProcessor

pytestmark = pytest.mark.unit


class TestInmemorySaleProcessor:

    def test_should_clean_and_enrich_sale_records(self) -> None:
        dataframe = pd.DataFrame(
            [
                {
                    sale_columns.order_id: "1",
                    sale_columns.customer_name: "Alice",
                    sale_columns.product_name: "Chair",
                    sale_columns.category: "Furniture",
                    sale_columns.quantity: "2",
                    sale_columns.unit_price: "10",
                    sale_columns.order_date: "2026-01-10",
                    sale_columns.country: "USA",
                },
                {
                    sale_columns.order_id: "1",
                    sale_columns.customer_name: "Alice",
                    sale_columns.product_name: "Chair",
                    sale_columns.category: "Furniture",
                    sale_columns.quantity: "2",
                    sale_columns.unit_price: "10",
                    sale_columns.order_date: "2026-01-10",
                    sale_columns.country: "USA",
                },
                {
                    sale_columns.order_id: "2",
                    sale_columns.customer_name: "Bob",
                    sale_columns.product_name: "Desk",
                    sale_columns.category: "Electronics",
                    sale_columns.quantity: "",
                    sale_columns.unit_price: "20",
                    sale_columns.order_date: "2026-01-11",
                    sale_columns.country: "Canada",
                },
                {
                    sale_columns.order_id: "3",
                    sale_columns.customer_name: "Carol",
                    sale_columns.product_name: "Lamp",
                    sale_columns.category: "Furniture",
                    sale_columns.quantity: "-1",
                    sale_columns.unit_price: "5",
                    sale_columns.order_date: "invalid",
                    sale_columns.country: "UK",
                },
            ]
        )

        processor = InmemorySaleProcessor()
        cleaned = processor.clean(dataframe)
        enriched = processor.enrich(cleaned)

        assert len(cleaned) == 2
        assert list(cleaned[sale_columns.order_id]) == [1, 2]
        assert list(enriched[sale_columns.total_price]) == [20.0, 20.0]
        assert list(enriched[sale_columns.year]) == [2026, 2026]


class TestInmemoryHouseProcessor:

    def test_should_clean_and_enrich_house_records(self) -> None:
        dataframe = pd.DataFrame(
            [
                {
                    house_columns.area_raw: " 3,310,000,000 ",
                    house_columns.room_raw: "2",
                    house_columns.parking_raw: "true",
                    house_columns.warehouse_raw: "false",
                    house_columns.elevator_raw: "true",
                    house_columns.address_raw: " Ostad Moein ",
                    house_columns.price_raw: "3310000000.0",
                    house_columns.price_usd_raw: "110333.33",
                },
                {
                    house_columns.area_raw: " 3,310,000,000 ",
                    house_columns.room_raw: "2",
                    house_columns.parking_raw: "true",
                    house_columns.warehouse_raw: "false",
                    house_columns.elevator_raw: "true",
                    house_columns.address_raw: " Ostad Moein ",
                    house_columns.price_raw: "3310000000.0",
                    house_columns.price_usd_raw: "110333.33",
                },
                {
                    house_columns.area_raw: "100",
                    house_columns.room_raw: "1",
                    house_columns.parking_raw: "false",
                    house_columns.warehouse_raw: "false",
                    house_columns.elevator_raw: "false",
                    house_columns.address_raw: " Noor ",
                    house_columns.price_raw: "1000",
                    house_columns.price_usd_raw: "",
                },
                {
                    house_columns.area_raw: "0",
                    house_columns.room_raw: "1",
                    house_columns.parking_raw: "false",
                    house_columns.warehouse_raw: "false",
                    house_columns.elevator_raw: "false",
                    house_columns.address_raw: "Invalid",
                    house_columns.price_raw: "10",
                    house_columns.price_usd_raw: "1",
                },
            ]
        )

        processor = InmemoryHouseProcessor()
        cleaned = processor.clean(dataframe)
        enriched = processor.enrich(cleaned)

        assert len(cleaned) == 2
        assert list(cleaned[house_columns.address]) == ["Ostad Moein", "Noor"]
        assert house_columns.listing_key in enriched.columns
        assert list(enriched[house_columns.price_per_square_meter]) == [1.0, 10.0]
