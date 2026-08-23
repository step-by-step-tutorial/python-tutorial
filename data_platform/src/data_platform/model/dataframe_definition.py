from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DataframeDefinition:
    schema: Any = None
    required_columns: frozenset[str] = frozenset()
