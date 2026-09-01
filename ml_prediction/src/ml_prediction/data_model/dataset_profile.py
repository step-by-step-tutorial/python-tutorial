from dataclasses import dataclass

from ml_prediction.config.settings_types import TaskType


@dataclass(frozen=True)
class DatasetProfile:
    target_column: str
    task_type: TaskType
    dataset_filename: str
    model_filename: str
    prediction_filename: str
    prediction_column: str
    experiment_filename: str
    data_lake_bucket: str
    data_lake_prefix: str
