from dataclasses import asdict, dataclass
from typing import Any

from dataset.house.columns import HOUSE_COLUMNS as model
from transformation.conversion.type_converter import convert_to_integer, convert_to_optional_float, \
    normalize_optional_text


@dataclass(frozen=True)
class HouseEvent:
    area: float
    room: int
    parking: bool | None
    warehouse: bool | None
    elevator: bool | None
    address: str | None
    price: float
    price_usd: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, row: dict[str, str]) -> "HouseEvent":
        return cls(
            area=float(row[model.area_raw]),
            room=convert_to_integer(row.get(model.room_raw)),
            parking=row.get(model.parking_raw) == "True" if row.get(model.parking_raw) is not None else None,
            warehouse=row.get(model.warehouse_raw) == "True" if row.get(model.warehouse_raw) is not None else None,
            elevator=row.get(model.elevator_raw) == "True" if row.get(model.elevator_raw) is not None else None,
            address=normalize_optional_text(row.get(model.address_raw)),
            price=float(row[model.price_raw]),
            price_usd=convert_to_optional_float(row.get(model.price_usd_raw))
        )
