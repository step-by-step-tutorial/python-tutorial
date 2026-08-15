from __future__ import annotations


def build_schema():
    from pyspark.sql.types import BooleanType, DoubleType, LongType, StringType, StructField, StructType

    from dataset.house.columns import house_columns as c

    return StructType([
        StructField(c.area_raw, DoubleType(), nullable=False),
        StructField(c.room_raw, LongType(), nullable=False),
        StructField(c.parking_raw, BooleanType(), nullable=True),
        StructField(c.warehouse_raw, BooleanType(), nullable=True),
        StructField(c.elevator_raw, BooleanType(), nullable=True),
        StructField(c.address_raw, StringType(), nullable=True),
        StructField(c.price_raw, DoubleType(), nullable=False),
        StructField(c.price_usd_raw, DoubleType(), nullable=True),
    ])

