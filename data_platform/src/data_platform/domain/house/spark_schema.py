def build_schema():
    from pyspark.sql.types import BooleanType, DoubleType, LongType, StringType, StructField, StructType

    from data_platform.domain.house.attribute import HOUSE_ATTRIBUTE

    return StructType([
        StructField(HOUSE_ATTRIBUTE.area_raw, DoubleType(), nullable=False),
        StructField(HOUSE_ATTRIBUTE.room_raw, LongType(), nullable=False),
        StructField(HOUSE_ATTRIBUTE.parking_raw, BooleanType(), nullable=True),
        StructField(HOUSE_ATTRIBUTE.warehouse_raw, BooleanType(), nullable=True),
        StructField(HOUSE_ATTRIBUTE.elevator_raw, BooleanType(), nullable=True),
        StructField(HOUSE_ATTRIBUTE.address_raw, StringType(), nullable=True),
        StructField(HOUSE_ATTRIBUTE.price_raw, DoubleType(), nullable=False),
        StructField(HOUSE_ATTRIBUTE.price_usd_raw, DoubleType(), nullable=True),
    ])

