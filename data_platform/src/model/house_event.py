from dataclasses import asdict, dataclass
from typing import Any

from dataset.house.model import model
from transformation.conversion.type_converter import convert_to_integer, convert_to_optional_float, normalize_optional_text


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
            area=float(row[model.AREA_RAW]),
            room=convert_to_integer(row.get(model.ROOM_RAW)),
            parking=row.get(model.PARKING_RAW) == "True" if row.get(model.PARKING_RAW) is not None else None,
            warehouse=row.get(model.WAREHOUSE_RAW) == "True" if row.get(model.WAREHOUSE_RAW) is not None else None,
            elevator=row.get(model.ELEVATOR_RAW) == "True" if row.get(model.ELEVATOR_RAW) is not None else None,
            address=normalize_optional_text(row.get(model.ADDRESS_RAW)),
            price=float(row[model.PRICE_RAW]),
            price_usd=convert_to_optional_float(row.get(model.PRICE_USD_RAW))
        )
