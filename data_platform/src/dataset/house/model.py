from dataset.house.columns import HouseColumns, house_columns as model
from dataset.house.spark_schema import build_schema

HOUSE_COLUMNS = model


required_columns = frozenset(
    {
        model.area_raw,
        model.room_raw,
        model.parking_raw,
        model.warehouse_raw,
        model.elevator_raw,
        model.address_raw,
        model.price_raw,
        model.price_usd_raw,
    }
)

all_columns: tuple[str, ...] = (
    model.area_raw,
    model.room_raw,
    model.parking_raw,
    model.warehouse_raw,
    model.elevator_raw,
    model.address_raw,
    model.price_raw,
    model.price_usd_raw,
    model.area,
    model.room,
    model.parking,
    model.warehouse,
    model.elevator,
    model.address,
    model.price,
    model.price_usd,
)

def get_struct_type():
    return build_schema()
