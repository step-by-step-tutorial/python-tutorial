from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ReportModel:
    name: str
    data: Any
