from __future__ import annotations


def build_schema():
    from pyspark.sql.types import DoubleType, LongType, StringType, StructField, StructType

    from dataset.sale.columns import sale_columns as c

    return StructType(
        [
            StructField(c.order_id, LongType(), nullable=False),
            StructField(c.customer_name, StringType(), nullable=False),
            StructField(c.product_name, StringType(), nullable=False),
            StructField(c.category, StringType(), nullable=False),
            StructField(c.quantity, DoubleType(), nullable=True),
            StructField(c.unit_price, DoubleType(), nullable=True),
            StructField(c.order_date, StringType(), nullable=True),
            StructField(c.country, StringType(), nullable=False),
        ]
    )

