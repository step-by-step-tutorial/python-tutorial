from dataclasses import dataclass

from pyspark.sql.types import BooleanType, DoubleType, LongType, StringType, StructField, StructType


@dataclass(frozen=True)
class DatasetModel:
    AREA_RAW: str = "Area"
    ROOM_RAW: str = "Room"
    PARKING_RAW: str = "Parking"
    WAREHOUSE_RAW: str = "Warehouse"
    ELEVATOR_RAW: str = "Elevator"
    ADDRESS_RAW: str = "Address"
    PRICE_RAW: str = "Price"
    PRICE_USD_RAW: str = "Price(USD)"
    AREA: str = "area"
    ROOM: str = "room"
    PARKING: str = "parking"
    WAREHOUSE: str = "warehouse"
    ELEVATOR: str = "elevator"
    ADDRESS: str = "address"
    PRICE: str = "price"
    PRICE_USD: str = "price_usd"
    LISTING_KEY: str = "listing_key"
    PRICE_PER_SQUARE_METER: str = "price_per_square_meter"
    PRICE_USD_PER_SQUARE_METER: str = "price_usd_per_square_meter"


model = DatasetModel()

required_columns = frozenset(
    {
        model.AREA_RAW,
        model.ROOM_RAW,
        model.PARKING_RAW,
        model.WAREHOUSE_RAW,
        model.ELEVATOR_RAW,
        model.ADDRESS_RAW,
        model.PRICE_RAW,
        model.PRICE_USD_RAW
    }
)

all_columns: tuple[str, ...] = (
    model.AREA_RAW,
    model.ROOM_RAW,
    model.PARKING_RAW,
    model.WAREHOUSE_RAW,
    model.ELEVATOR_RAW,
    model.ADDRESS_RAW,
    model.PRICE_RAW,
    model.PRICE_USD_RAW,
    model.AREA,
    model.ROOM,
    model.PARKING,
    model.WAREHOUSE,
    model.ELEVATOR,
    model.ADDRESS,
    model.PRICE,
    model.PRICE_USD
)

struct_type = StructType([
    StructField(model.AREA_RAW, DoubleType(), nullable=False),
    StructField(model.ROOM_RAW, LongType(), nullable=False),
    StructField(model.PARKING_RAW, BooleanType(), nullable=True),
    StructField(model.WAREHOUSE_RAW, BooleanType(), nullable=True),
    StructField(model.ELEVATOR_RAW, BooleanType(), nullable=True),
    StructField(model.ADDRESS_RAW, StringType(), nullable=True),
    StructField(model.PRICE_RAW, DoubleType(), nullable=False),
    StructField(model.PRICE_USD_RAW, DoubleType(), nullable=True),
])
