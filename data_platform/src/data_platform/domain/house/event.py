from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class HouseEvent:
    values: Mapping[str, Any]

    @property
    def property_id(self) -> str | None:
        value = self.values.get("property_id")
        return None if value is None else str(value)

    def to_dict(self) -> dict[str, Any]:
        return dict(self.values)
