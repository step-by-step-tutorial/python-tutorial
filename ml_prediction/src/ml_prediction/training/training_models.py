from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ml_prediction.evaluation.model_evaluator import RegressionMetrics


@dataclass(frozen=True)
class TrainingOutput:
    model_path: Path
    baseline_validation_metrics: RegressionMetrics
    validation_metrics: RegressionMetrics
    test_metrics: RegressionMetrics
    report_path: Path | None = None


@dataclass(frozen=True)
class DatasetPartition:
    features: pd.DataFrame
    target: pd.Series


@dataclass(frozen=True)
class DatasetPartitions:
    train: DatasetPartition
    validation: DatasetPartition
    test: DatasetPartition
