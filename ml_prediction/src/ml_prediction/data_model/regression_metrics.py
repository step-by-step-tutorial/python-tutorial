from dataclasses import dataclass


@dataclass(frozen=True)
class RegressionMetrics:
    mean_absolute_error: float
    root_mean_squared_error: float
    r2_score: float
