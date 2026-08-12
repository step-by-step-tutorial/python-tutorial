from dataclasses import asdict, dataclass
from typing import Any

from dataset.house.schema import dataset_model_instance
from util.csv_utils import convert_to_integer, convert_to_optional_float, normalize_optional_text


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
            area=float(row[dataset_model_instance.AREA_RAW]),
            room=convert_to_integer(row.get(dataset_model_instance.ROOM_RAW)),
            parking=row.get(dataset_model_instance.PARKING_RAW) == "True" if row.get(dataset_model_instance.PARKING_RAW) is not None else None,
            warehouse=row.get(dataset_model_instance.WAREHOUSE_RAW) == "True" if row.get(dataset_model_instance.WAREHOUSE_RAW) is not None else None,
            elevator=row.get(dataset_model_instance.ELEVATOR_RAW) == "True" if row.get(dataset_model_instance.ELEVATOR_RAW) is not None else None,
            address=normalize_optional_text(row.get(dataset_model_instance.ADDRESS_RAW)),
            price=float(row[dataset_model_instance.PRICE_RAW]),
            price_usd=convert_to_optional_float(row.get(dataset_model_instance.PRICE_USD_RAW))
        )