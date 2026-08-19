

def build_schema():
    from pyspark.sql.types import DoubleType, LongType, StringType, StructField, StructType

    from dataset.sale.attribute import SALE_ATTRIBUTE

    return StructType(
        [
            StructField(SALE_ATTRIBUTE.order_id, LongType(), nullable=False),
            StructField(SALE_ATTRIBUTE.customer_name, StringType(), nullable=False),
            StructField(SALE_ATTRIBUTE.product_name, StringType(), nullable=False),
            StructField(SALE_ATTRIBUTE.category, StringType(), nullable=False),
            StructField(SALE_ATTRIBUTE.quantity, DoubleType(), nullable=True),
            StructField(SALE_ATTRIBUTE.unit_price, DoubleType(), nullable=True),
            StructField(SALE_ATTRIBUTE.order_date, StringType(), nullable=True),
            StructField(SALE_ATTRIBUTE.country, StringType(), nullable=False),
        ]
    )

