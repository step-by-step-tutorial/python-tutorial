from dataclasses import dataclass

from ml_prediction.data_model.metrics import Metrics

@dataclass(frozen=True)
class RegressionMetrics(Metrics):
    mean_absolute_error: float
    root_mean_squared_error: float
    r2_score: float

    def to_string(self) -> str:
        return (
            f"mae={self.mean_absolute_error:.2f} "
            f"rmse={self.root_mean_squared_error:.2f} "
            f"r2={self.r2_score:.4f}"
        )
