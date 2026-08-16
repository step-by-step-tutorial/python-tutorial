from __future__ import annotations

import os
import sys

import pandas as pd
import pytest
from pyspark.sql import SparkSession

from dataset.house.columns import house_columns
from dataset.sale.columns import sale_columns
from processor.spark.house_processor import SparkHouseProcessor
from processor.spark.sale_processor import SparkSaleProcessor

pytestmark = pytest.mark.spark


@pytest.fixture(scope="module")
def spark_session() -> SparkSession:
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    session = (
        SparkSession.builder
        .master("local[1]")
        .appName("processor-tests")
        .config("spark.ui.enabled", "false")
        .config("spark.pyspark.python", sys.executable)
        .config("spark.pyspark.driver.python", sys.executable)
        .getOrCreate()
    )
    yield session
    session.stop()


class TestSparkSaleProcessor:

    def test_should_clean_and_enrich_sale_records(self, spark_session: SparkSession) -> None:
        dataframe = spark_session.createDataFrame(
            pd.DataFrame(
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
        )

        processor = SparkSaleProcessor()
        cleaned = processor.clean(dataframe)
        enriched = processor.enrich(cleaned)

        assert cleaned.count() == 2
        assert [row[sale_columns.order_id] for row in cleaned.orderBy(sale_columns.order_id).collect()] == ["1", "2"]
        assert [row[sale_columns.total_price] for row in enriched.orderBy(sale_columns.order_id).collect()] == [20.0, 20.0]


class TestSparkHouseProcessor:

    def test_should_clean_and_enrich_house_records(self, spark_session: SparkSession) -> None:
        dataframe = spark_session.createDataFrame(
            pd.DataFrame(
                [
                    {
                        house_columns.area_raw: "200",
                        house_columns.room_raw: "2",
                        house_columns.parking_raw: "true",
                        house_columns.warehouse_raw: "false",
                        house_columns.elevator_raw: "true",
                        house_columns.address_raw: " Ostad Moein ",
                        house_columns.price_raw: "2000",
                        house_columns.price_usd_raw: "50",
                    },
                    {
                        house_columns.area_raw: "200",
                        house_columns.room_raw: "2",
                        house_columns.parking_raw: "true",
                        house_columns.warehouse_raw: "false",
                        house_columns.elevator_raw: "true",
                        house_columns.address_raw: " Ostad Moein ",
                        house_columns.price_raw: "2000",
                        house_columns.price_usd_raw: "50",
                    },
                    {
                        house_columns.area_raw: "100",
                        house_columns.room_raw: "1",
                        house_columns.parking_raw: "false",
                        house_columns.warehouse_raw: "false",
                        house_columns.elevator_raw: "false",
                        house_columns.address_raw: " Noor ",
                        house_columns.price_raw: "1000",
                        house_columns.price_usd_raw: "25",
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
        )

        processor = SparkHouseProcessor()
        cleaned = processor.clean(dataframe)
        enriched = processor.enrich(cleaned)

        assert cleaned.count() == 2
        assert [row[house_columns.address] for row in cleaned.orderBy(house_columns.address).collect()] == ["Noor", "Ostad Moein"]
        assert house_columns.listing_key in enriched.columns
