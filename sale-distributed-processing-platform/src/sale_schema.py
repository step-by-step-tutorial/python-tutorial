
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)


SALE_SCHEMA = StructType(
    [
        StructField("order_id", IntegerType(), nullable=False),
        StructField("customer_name", StringType(), nullable=False),
        StructField("product_name", StringType(), nullable=False),
        StructField("category", StringType(), nullable=False),
        StructField("quantity", DoubleType(), nullable=True),
        StructField("unit_price", DoubleType(), nullable=True),
        StructField("order_date", StringType(), nullable=True),
        StructField("country", StringType(), nullable=False),
    ]
)
