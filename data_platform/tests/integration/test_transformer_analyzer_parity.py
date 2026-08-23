
import os
import sys
from typing import cast

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from pyspark import SparkContext
from pyspark.sql import SparkSession

from data_platform.model.house_attribute import HOUSE_ATTRIBUTE
from data_platform.model.sale_attribute import SALE_ATTRIBUTE
from data_platform.data_transformer.inmemory_house_transformer import InmemoryHouseTransformer
from data_platform.data_transformer.inmemory_sale_transformer import InmemorySaleTransformer
from data_platform.data_transformer.spark_house_transformer import SparkHouseTransformer
from data_platform.data_transformer.spark_sale_transformer import SparkSaleTransformer
from data_platform.analyzer.inmemory_house_analyzer import InmemoryHouseAnalyzer
from data_platform.analyzer.inmemory_sale_analyzer import InmemorySaleAnalyzer
from data_platform.analyzer.spark_house_analyzer import SparkHouseAnalyzer
from data_platform.analyzer.spark_sale_analyzer import SparkSaleAnalyzer

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
        .appName("transformer-analyzer-parity-tests")
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


def _normalize(frame: pd.DataFrame, sort_columns: list[str] | None = None) -> pd.DataFrame:
    normalized = frame.copy()

    for column in normalized.columns:
        if column == SALE_ATTRIBUTE.order_id:
            normalized[column] = normalized[column].astype("string")
        if column == SALE_ATTRIBUTE.order_date:
            dates = cast(pd.Series, pd.to_datetime(normalized[column], errors="coerce"))
            normalized[column] = dates.dt.strftime("%Y-%m-%d")
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


class TestSaleTransformerAnalyzerParity:

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

        in_memory_cleaned = InmemorySaleTransformer().clean(raw)
        in_memory = InmemorySaleTransformer().enrich(in_memory_cleaned)
        spark_cleaned = SparkSaleTransformer().clean(spark_session.createDataFrame(raw))
        spark_enriched = SparkSaleTransformer().enrich(spark_cleaned)
        spark = spark_enriched.toPandas()

        _compare_frames(in_memory, spark, sort_columns=[SALE_ATTRIBUTE.order_id])

        in_memory_analysis = InmemorySaleAnalyzer().analyze(in_memory)
        spark_analysis = SparkSaleAnalyzer().analyze(spark_enriched)

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


class TestHouseTransformerAnalyzerParity:

    def test_should_match_between_pandas_and_spark(self, spark_session: SparkSession) -> None:
        raw = pd.DataFrame(
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
                    HOUSE_ATTRIBUTE.area_raw: "100",
                    HOUSE_ATTRIBUTE.room_raw: "1",
                    HOUSE_ATTRIBUTE.parking_raw: "false",
                    HOUSE_ATTRIBUTE.warehouse_raw: "false",
                    HOUSE_ATTRIBUTE.elevator_raw: "false",
                    HOUSE_ATTRIBUTE.address_raw: " Oak Avenue ",
                    HOUSE_ATTRIBUTE.price_raw: "1000",
                    HOUSE_ATTRIBUTE.price_usd_raw: "25",
                },
            ]
        )

        in_memory_cleaned = InmemoryHouseTransformer().clean(raw)
        in_memory = InmemoryHouseTransformer().enrich(in_memory_cleaned)
        spark_cleaned = SparkHouseTransformer().clean(spark_session.createDataFrame(raw))
        spark_enriched = SparkHouseTransformer().enrich(spark_cleaned)
        spark = spark_enriched.toPandas()

        _compare_frames(in_memory, spark, sort_columns=[HOUSE_ATTRIBUTE.address])

        in_memory_analysis = InmemoryHouseAnalyzer().analyze(in_memory)
        spark_analysis = SparkHouseAnalyzer().analyze(spark_enriched)

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
