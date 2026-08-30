from dataclasses import dataclass
import pandas as pd

from ml_prediction.model.experiment_result import ExperimentResult


# Kept as an alias so existing training and presentation callers retain their API.
TrainingOutput = ExperimentResult


@dataclass(frozen=True)
class DatasetPartition:
    features: pd.DataFrame
    target: pd.Series


@dataclass(frozen=True)
class DatasetPartitions:
    train: DatasetPartition
    validation: DatasetPartition
    test: DatasetPartition
