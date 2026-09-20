from dataclasses import dataclass

from ml_prediction.data_model.metrics import Metrics

@dataclass(frozen=True)
class ClassificationMetrics(Metrics):
    accuracy: float
    precision: float
    recall: float
    f1_score: float

    def to_string(self) -> str:
        return (
            f"accuracy={self.accuracy:.4f} "
            f"precision={self.precision:.4f} "
            f"recall={self.recall:.4f} "
            f"f1={self.f1_score:.4f}"
        )
