from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MappedEvent:
    key: str | None
    payload: dict[str, Any]

