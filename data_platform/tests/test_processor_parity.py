from __future__ import annotations

import os
import sys

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from pyspark.sql import SparkSession

from dataset.house.columns import house_columns
from dataset.sale.columns import sale_columns
from processor.inmemory.house_processor import InmemoryHouseProcessor
from processor.inmemory.sale_processor import InmemorySaleProcessor
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
        if column == sale_columns.order_id:
            normalized[column] = normalized[column].astype("string")
        if column == sale_columns.order_date:
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
            ]
        )

        in_memory_cleaned = InmemorySaleProcessor().clean(raw)
        in_memory = InmemorySaleProcessor().enrich(in_memory_cleaned)
        spark_cleaned = SparkSaleProcessor().clean(spark_session.createDataFrame(raw))
        spark_enriched = SparkSaleProcessor().enrich(spark_cleaned)
        spark = spark_enriched.toPandas()

        _compare_frames(in_memory, spark, sort_columns=[sale_columns.order_id])

        in_memory_analysis = InmemorySaleProcessor().analyze(in_memory)
        spark_analysis = SparkSaleProcessor().analyze(spark_enriched)

        _compare_frames(
            in_memory_analysis["revenue_by_category"],
            spark_analysis["revenue_by_category"].toPandas(),
            sort_columns=[sale_columns.category],
        )
        _compare_frames(
            in_memory_analysis["revenue_by_country"],
            spark_analysis["revenue_by_country"].toPandas(),
            sort_columns=[sale_columns.country],
        )


class TestHouseProcessorParity:

    def test_should_match_between_pandas_and_spark(self, spark_session: SparkSession) -> None:
        raw = pd.DataFrame(
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
                    house_columns.area_raw: "100",
                    house_columns.room_raw: "1",
                    house_columns.parking_raw: "false",
                    house_columns.warehouse_raw: "false",
                    house_columns.elevator_raw: "false",
                    house_columns.address_raw: " Noor ",
                    house_columns.price_raw: "1000",
                    house_columns.price_usd_raw: "25",
                },
            ]
        )

        in_memory_cleaned = InmemoryHouseProcessor().clean(raw)
        in_memory = InmemoryHouseProcessor().enrich(in_memory_cleaned)
        spark_cleaned = SparkHouseProcessor().clean(spark_session.createDataFrame(raw))
        spark_enriched = SparkHouseProcessor().enrich(spark_cleaned)
        spark = spark_enriched.toPandas()

        _compare_frames(in_memory, spark, sort_columns=[house_columns.address])

        in_memory_analysis = InmemoryHouseProcessor().analyze(in_memory)
        spark_analysis = SparkHouseProcessor().analyze(spark_enriched)

        _compare_frames(
            in_memory_analysis["average_price_by_address"],
            spark_analysis["average_price_by_address"].toPandas(),
            sort_columns=[house_columns.address],
        )
        _compare_frames(
            in_memory_analysis["average_price_by_square_meter"],
            spark_analysis["average_price_per_square_meter_by_room"].toPandas().rename(
                columns={"average_price_per_square_meter": "average_price_by_square_meter"}
            ),
            sort_columns=[house_columns.room],
        )
