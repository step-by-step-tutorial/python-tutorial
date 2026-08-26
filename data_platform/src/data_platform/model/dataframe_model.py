from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DataFrameModel:
    schema: Any = None
    required_columns: frozenset[str] = frozenset()
