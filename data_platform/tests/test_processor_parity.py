from __future__ import annotations

import os
import sys

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from pyspark.sql import SparkSession

from dataset.house.attribute import HOUSE_ATTRIBUTE
from dataset.sale.attribute import SALE_ATTRIBUTE
from processor.inmemory.house_processor import InmemoryHouseProcessor
from processor.inmemory.sale_processor import InmemorySaleProcessor
from processor.spark.house_processor import SparkHouseProcessor
from processor.spark.sale_processor import SparkSaleProcessor

pytestmark = pytest.mark.spark_service


@pytest.fixture(scope="module")
def spark_session() -> SparkSession:
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    session = (
        SparkSession.builder
        .master("local[1]")
        .appName("processor-parity-tests")
        .config("spark.ui.enabled", "false")
        .config("spark.pyspark.python", sys.executable)
        .config("spark.pyspark.driver.python", sys.executable)
        .getOrCreate()
    )
    yield session
    session.stop()


def _normalize(frame: pd.DataFrame, sort_columns: list[str] | None = None) -> pd.DataFrame:
    normalized = frame.copy()

    for column in normalized.columns:
        if column == SALE_ATTRIBUTE.order_id:
            normalized[column] = normalized[column].astype("string")
        if column == SALE_ATTRIBUTE.order_date:
            normalized[column] = pd.to_datetime(normalized[column], errors="coerce").dt.strftime("%Y-%m-%d")
        else:
            normalized[column] = normalized[column]

    sort_columns = sort_columns or list(normalized.columns)
    return normalized.sort_values(by=sort_columns).reset_index(drop=True)


def _compare_frames(left: pd.DataFrame, right: pd.DataFrame, sort_columns: list[str] | None = None) -> None:
    assert_frame_equal(
        _normalize(left, sort_columns=sort_columns),
        _normalize(right, sort_columns=sort_columns),
        check_dtype=False,
        check_like=True,
    )


class TestSaleProcessorParity:

    def test_should_match_between_pandas_and_spark(self, spark_session: SparkSession) -> None:
        raw = pd.DataFrame(
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
            ]
        )

        in_memory_cleaned = InmemorySaleProcessor().clean(raw)
        in_memory = InmemorySaleProcessor().enrich(in_memory_cleaned)
        spark_cleaned = SparkSaleProcessor().clean(spark_session.createDataFrame(raw))
        spark_enriched = SparkSaleProcessor().enrich(spark_cleaned)
        spark = spark_enriched.toPandas()

        _compare_frames(in_memory, spark, sort_columns=[SALE_ATTRIBUTE.order_id])

        in_memory_analysis = InmemorySaleProcessor().analyze(in_memory)
        spark_analysis = SparkSaleProcessor().analyze(spark_enriched)

        _compare_frames(
            in_memory_analysis["revenue_by_category"],
            spark_analysis["revenue_by_category"].toPandas(),
            sort_columns=[SALE_ATTRIBUTE.category],
        )
        _compare_frames(
            in_memory_analysis["revenue_by_country"],
            spark_analysis["revenue_by_country"].toPandas(),
            sort_columns=[SALE_ATTRIBUTE.country],
        )


class TestHouseProcessorParity:

    def test_should_match_between_pandas_and_spark(self, spark_session: SparkSession) -> None:
        raw = pd.DataFrame(
            [
                {
                    HOUSE_ATTRIBUTE.area_raw: "200",
                    HOUSE_ATTRIBUTE.room_raw: "2",
                    HOUSE_ATTRIBUTE.parking_raw: "true",
                    HOUSE_ATTRIBUTE.warehouse_raw: "false",
                    HOUSE_ATTRIBUTE.elevator_raw: "true",
                    HOUSE_ATTRIBUTE.address_raw: " Ostad Moein ",
                    HOUSE_ATTRIBUTE.price_raw: "2000",
                    HOUSE_ATTRIBUTE.price_usd_raw: "50",
                },
                {
                    HOUSE_ATTRIBUTE.area_raw: "100",
                    HOUSE_ATTRIBUTE.room_raw: "1",
                    HOUSE_ATTRIBUTE.parking_raw: "false",
                    HOUSE_ATTRIBUTE.warehouse_raw: "false",
                    HOUSE_ATTRIBUTE.elevator_raw: "false",
                    HOUSE_ATTRIBUTE.address_raw: " Noor ",
                    HOUSE_ATTRIBUTE.price_raw: "1000",
                    HOUSE_ATTRIBUTE.price_usd_raw: "25",
                },
            ]
        )

        in_memory_cleaned = InmemoryHouseProcessor().clean(raw)
        in_memory = InmemoryHouseProcessor().enrich(in_memory_cleaned)
        spark_cleaned = SparkHouseProcessor().clean(spark_session.createDataFrame(raw))
        spark_enriched = SparkHouseProcessor().enrich(spark_cleaned)
        spark = spark_enriched.toPandas()

        _compare_frames(in_memory, spark, sort_columns=[HOUSE_ATTRIBUTE.address])

        in_memory_analysis = InmemoryHouseProcessor().analyze(in_memory)
        spark_analysis = SparkHouseProcessor().analyze(spark_enriched)

        _compare_frames(
            in_memory_analysis["average_price_by_address"],
            spark_analysis["average_price_by_address"].toPandas(),
            sort_columns=[HOUSE_ATTRIBUTE.address],
        )
        _compare_frames(
            in_memory_analysis["average_price_by_square_meter"],
            spark_analysis["average_price_per_square_meter_by_room"].toPandas().rename(
                columns={"average_price_per_square_meter": "average_price_by_square_meter"}
            ),
            sort_columns=[HOUSE_ATTRIBUTE.room],
        )
