
import os
import sys
from typing import Any, Generator

import pandas as pd
import pytest
from pyspark import SparkContext
from pyspark.sql import SparkSession

from data_platform.model.house_attribute import HOUSE_ATTRIBUTE
from data_platform.model.sale_attribute import SALE_ATTRIBUTE
from data_platform.processor.spark_house_processor import SparkHouseProcessor
from data_platform.processor.spark_sale_processor import SparkSaleProcessor

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def spark_session() -> SparkSession:
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    os.environ["SPARK_LOCAL_HOSTNAME"] = "localhost"
    os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"
    active_context = SparkContext._active_spark_context
    if active_context is not None:
        active_context.stop()
    SparkSession._instantiatedSession = None
    SparkSession._activeSession = None
    session = (
        SparkSession.builder
        .master("local[1]")
        .appName("processor-tests")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.local.ip", "127.0.0.1")
        .config("spark.executorEnv.PYSPARK_PYTHON", sys.executable)
        .config("spark.executorEnv.PYSPARK_DRIVER_PYTHON", sys.executable)
        .config("spark.pyspark.python", sys.executable)
        .config("spark.pyspark.driver.python", sys.executable)
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.default.parallelism", "1")
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
        )

        processor = SparkSaleProcessor()
        cleaned = processor.clean(dataframe)
        enriched = processor.enrich(cleaned)

        assert cleaned.count() == 2
        assert [row[SALE_ATTRIBUTE.order_id] for row in cleaned.orderBy(SALE_ATTRIBUTE.order_id).collect()] == ["1", "2"]
        assert [row[SALE_ATTRIBUTE.total_price] for row in enriched.orderBy(SALE_ATTRIBUTE.order_id).collect()] == [20.0, 20.0]


class TestSparkHouseProcessor:

    def test_should_clean_and_enrich_house_records(self, spark_session: SparkSession) -> None:
        dataframe = spark_session.createDataFrame(
            pd.DataFrame(
                [
                    {
                        HOUSE_ATTRIBUTE.area_raw: "200",
                        HOUSE_ATTRIBUTE.room_raw: "2",
                        HOUSE_ATTRIBUTE.parking_raw: "true",
                        HOUSE_ATTRIBUTE.warehouse_raw: "false",
                        HOUSE_ATTRIBUTE.elevator_raw: "true",
                        HOUSE_ATTRIBUTE.address_raw: " Main Street ",
                        HOUSE_ATTRIBUTE.price_raw: "2000",
                        HOUSE_ATTRIBUTE.price_usd_raw: "50",
                    },
                    {
                        HOUSE_ATTRIBUTE.area_raw: "200",
                        HOUSE_ATTRIBUTE.room_raw: "2",
                        HOUSE_ATTRIBUTE.parking_raw: "true",
                        HOUSE_ATTRIBUTE.warehouse_raw: "false",
                        HOUSE_ATTRIBUTE.elevator_raw: "true",
                        HOUSE_ATTRIBUTE.address_raw: " Main Street ",
                        HOUSE_ATTRIBUTE.price_raw: "2000",
                        HOUSE_ATTRIBUTE.price_usd_raw: "50",
                    },
                    {
                        HOUSE_ATTRIBUTE.area_raw: "100",
                        HOUSE_ATTRIBUTE.room_raw: "1",
                        HOUSE_ATTRIBUTE.parking_raw: "false",
                        HOUSE_ATTRIBUTE.warehouse_raw: "false",
                        HOUSE_ATTRIBUTE.elevator_raw: "false",
                        HOUSE_ATTRIBUTE.address_raw: " Oak Avenue ",
                        HOUSE_ATTRIBUTE.price_raw: "1000",
                        HOUSE_ATTRIBUTE.price_usd_raw: "25",
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
        )

        processor = SparkHouseProcessor()
        cleaned = processor.clean(dataframe)
        enriched = processor.enrich(cleaned)

        assert cleaned.count() == 2
        assert [row[HOUSE_ATTRIBUTE.address] for row in cleaned.orderBy(HOUSE_ATTRIBUTE.address).collect()] == ["Main Street", "Oak Avenue"]
        assert HOUSE_ATTRIBUTE.listing_key in enriched.columns
