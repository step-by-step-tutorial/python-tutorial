from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DataFrameDefinition:
    schema: Any = None
    required_columns: frozenset[str] = frozenset()
