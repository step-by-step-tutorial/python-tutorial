from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from ml_prediction.config.settings_types import TaskType
from ml_prediction.data_model.datalake_settings import DataLakeSettings

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class DatasetSource(StrEnum):
    LOCAL = "local"
    DOWNLOAD = "download"


@dataclass(frozen=True)
class AppSettings:
    data_dir: Path
    model_dir: Path
    target_column: str
    validation_size: float
    test_size: float
    random_state: int
    data_lake: DataLakeSettings
    task_type: TaskType = TaskType.REGRESSION
    model_type: str = "random_forest"
    n_estimators: int = 200
    n_jobs: int = -1
    max_depth: int | None = None
    min_samples_split: int = 2
    min_samples_leaf: int = 1
    max_features: int | float | str | None = 1.0
    bootstrap: bool = True
    dataset_source: DatasetSource = DatasetSource.LOCAL
    report_dir: Path = PROJECT_ROOT / "reports"
    dataset_name: str = ""
    dataset_filename: str = ""
    model_filename: str = ""
    prediction_filename: str = ""
    prediction_column: str = ""
    experiment_filename: str = "experiments.csv"
    mlflow_tracking_uri: str = ""
    mlflow_experiment_prefix: str = "ml_prediction"
    mlflow_enabled: bool = False
    mlflow_required: bool = False
