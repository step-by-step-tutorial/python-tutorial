from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Report:
    name: str
    data: Any
