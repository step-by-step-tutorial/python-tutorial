from dataclasses import dataclass
from typing import Any

from sklearn.pipeline import Pipeline


@dataclass(frozen=True)
class ClassificationSelection:
    pipeline: Pipeline
    parameters: dict[str, Any]
    f1_score: float
