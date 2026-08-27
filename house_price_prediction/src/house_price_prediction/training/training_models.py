from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from house_price_prediction.evaluation.model_evaluator import RegressionMetrics


@dataclass(frozen=True)
class TrainingResult:
    model_path: Path
    baseline_metrics: RegressionMetrics
    validation_metrics: RegressionMetrics
    model_metrics: RegressionMetrics


@dataclass(frozen=True)
class DatasetSplit:
    train_features: pd.DataFrame
    validation_features: pd.DataFrame
    test_features: pd.DataFrame
    train_target: pd.Series
    validation_target: pd.Series
    test_target: pd.Series
