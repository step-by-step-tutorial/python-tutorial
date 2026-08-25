def build_schema():
    from pyspark.sql.types import DoubleType, LongType, StringType, StructField, StructType

    from data_platform.domain.sale.attribute import attribute

    return StructType(
        [
            StructField(attribute.order_id, LongType(), nullable=False),
            StructField(attribute.customer_name, StringType(), nullable=False),
            StructField(attribute.product_name, StringType(), nullable=False),
            StructField(attribute.category, StringType(), nullable=False),
            StructField(attribute.quantity, DoubleType(), nullable=True),
            StructField(attribute.unit_price, DoubleType(), nullable=True),
            StructField(attribute.order_date, StringType(), nullable=True),
            StructField(attribute.country, StringType(), nullable=False),
        ]
    )

