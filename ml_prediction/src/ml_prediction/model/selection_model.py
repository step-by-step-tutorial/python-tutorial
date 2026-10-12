from dataclasses import dataclass
from typing import Any

from sklearn.pipeline import Pipeline


@dataclass(frozen=True)
class SelectionModel:
    pipeline: Pipeline
    parameters: dict[str, Any]
    metric: str
    score: float
