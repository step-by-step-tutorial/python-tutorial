from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ml_platform.config.task_type import TaskType


@dataclass(frozen=True)
class PredictionModel:
    dataframe: pd.DataFrame
    predictions: pd.Series
    source_path: Path
    prediction_column: str
    task_type: TaskType

    def to_dataframe(self) -> pd.DataFrame:
        return self.dataframe.assign(**{self.prediction_column: self.predictions})

    def to_string(self) -> str:
        fields = [f"rows={len(self.predictions)}", f"column={self.prediction_column}"]
        if self.task_type is TaskType.REGRESSION:
            fields += [
                f"min={self.predictions.min():.2f}",
                f"max={self.predictions.max():.2f}",
                f"mean={self.predictions.mean():.2f}",
            ]
        return " ".join(fields)
