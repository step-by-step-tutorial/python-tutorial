from dataclasses import dataclass

from ml_prediction.config.task_type import TaskType
from ml_prediction.model.feature_set_model import FeatureSetModel


@dataclass(frozen=True)
class DatasetProfileModel:
    name: str
    task_type: TaskType
    target_column: str
    prediction_column: str
    features: FeatureSetModel
    data_lake_bucket: str
    data_lake_prefix: str
