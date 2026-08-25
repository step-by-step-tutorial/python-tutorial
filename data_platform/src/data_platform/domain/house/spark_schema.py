def build_schema():
    from pyspark.sql.types import BooleanType, DoubleType, LongType, StringType, StructField, StructType

    from data_platform.domain.house.attribute import attribute

    return StructType([
        StructField(attribute.area_raw, DoubleType(), nullable=False),
        StructField(attribute.room_raw, LongType(), nullable=False),
        StructField(attribute.parking_raw, BooleanType(), nullable=True),
        StructField(attribute.warehouse_raw, BooleanType(), nullable=True),
        StructField(attribute.elevator_raw, BooleanType(), nullable=True),
        StructField(attribute.address_raw, StringType(), nullable=True),
        StructField(attribute.price_raw, DoubleType(), nullable=False),
        StructField(attribute.price_usd_raw, DoubleType(), nullable=True),
    ])

