from dataclasses import asdict, dataclass
from typing import Any


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

