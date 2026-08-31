from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class PredictionOutput:
    dataframe: pd.DataFrame
    predictions: pd.Series
    source_path: Path
    report_path: Path | None = None
    prediction_column: str = "predicted_total_price"
