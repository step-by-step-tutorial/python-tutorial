from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType


@dataclass(frozen=True)
class PredictionDto:
    dataframe: pd.DataFrame
    predictions: pd.Series
    source_path: Path
    prediction_column: str
    task_type: ExperimentTaskType
    audit_path: Path | None = None

    def to_string(self) -> str:
        fields = [
            f"source={self.source_path}",
            f"audit={self.audit_path}",
            f"rows={len(self.predictions)}",
            f"prediction_column={self.prediction_column}",
        ]
        if self.task_type is ExperimentTaskType.REGRESSION:
            fields.extend([
                f"min={float(self.predictions.min()):.2f}",
                f"max={float(self.predictions.max()):.2f}",
                f"average={float(self.predictions.mean()):.2f}",
            ])
        return " ".join(fields)
