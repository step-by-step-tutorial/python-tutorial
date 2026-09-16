from dataclasses import dataclass
from typing import Any

from sklearn.pipeline import Pipeline


@dataclass(frozen=True)
class RegressionSelection:
    pipeline: Pipeline
    parameters: dict[str, Any]
    mean_absolute_error: float
