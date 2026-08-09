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


dataset_model_instance = DatasetModel()

REQUIRED_COLUMNS = frozenset(
    {
        dataset_model_instance.AREA_RAW,
        dataset_model_instance.ROOM_RAW,
        dataset_model_instance.PARKING_RAW,
        dataset_model_instance.WAREHOUSE_RAW,
        dataset_model_instance.ELEVATOR_RAW,
        dataset_model_instance.ADDRESS_RAW,
        dataset_model_instance.PRICE_RAW,
        dataset_model_instance.PRICE_USD_RAW
    }
)

ALL_COLUMNS: tuple[str, ...] = (
    dataset_model_instance.AREA_RAW,
    dataset_model_instance.ROOM_RAW,
    dataset_model_instance.PARKING_RAW,
    dataset_model_instance.WAREHOUSE_RAW,
    dataset_model_instance.ELEVATOR_RAW,
    dataset_model_instance.ADDRESS_RAW,
    dataset_model_instance.PRICE_RAW,
    dataset_model_instance.PRICE_USD_RAW,
    dataset_model_instance.AREA,
    dataset_model_instance.ROOM,
    dataset_model_instance.PARKING,
    dataset_model_instance.WAREHOUSE,
    dataset_model_instance.ELEVATOR,
    dataset_model_instance.ADDRESS,
    dataset_model_instance.PRICE,
    dataset_model_instance.PRICE_USD
)

DATAFRAME_SCHEMA = StructType([
    StructField(dataset_model_instance.AREA_RAW, DoubleType(), nullable=False),
    StructField(dataset_model_instance.ROOM_RAW, LongType(), nullable=False),
    StructField(dataset_model_instance.PARKING_RAW, BooleanType(), nullable=True),
    StructField(dataset_model_instance.WAREHOUSE_RAW, BooleanType(), nullable=True),
    StructField(dataset_model_instance.ELEVATOR_RAW, BooleanType(), nullable=True),
    StructField(dataset_model_instance.ADDRESS_RAW, StringType(), nullable=True),
    StructField(dataset_model_instance.PRICE_RAW, DoubleType(), nullable=False),
    StructField(dataset_model_instance.PRICE_USD_RAW, DoubleType(), nullable=True),
])
