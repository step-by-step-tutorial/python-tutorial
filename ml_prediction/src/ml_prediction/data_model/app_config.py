from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType
from ml_prediction.data_model.datalake_config import DataLakeconfig
from ml_prediction.data_model.model_parameters import ModelParameters


class DatasetSource(StrEnum):
    LOCAL = "local"
    DOWNLOAD = "download"


@dataclass(frozen=True)
class AppConfig:
    data_root: Path
    model_root: Path
    target_column: str
    validation_size: float
    test_size: float
    random_state: int
    data_lake: DataLakeconfig
    task_type: ExperimentTaskType = ExperimentTaskType.REGRESSION
    model_type: str = "random_forest"
    n_estimators: int = 200
    n_jobs: int = -1
    max_depth: int | None = None
    min_samples_split: int = 2
    min_samples_leaf: int = 1
    max_features: int | float | str | None = 1.0
    bootstrap: bool = True
    dataset_source: DatasetSource = DatasetSource.LOCAL
    audit_root: Path = Path("audit_log")
    audit_filename_template: str = "{dataset_name}_{operation}_{run_id}.csv"
    prediction_audit_filename_template: str = "{dataset_name}_prediction_{run_id}.csv"
    comparison_dirname: str = "comparison"
    actual_vs_predicted_filename: str = "actual_vs_predicted.png"
    residual_vs_predicted_filename: str = "residual_vs_predicted.png"
    feature_importance_filename: str = "feature_importance.png"
    confusion_matrix_filename: str = "confusion_matrix.png"
    validation_mae_filename: str = "validation_mae_comparison.png"
    validation_rmse_filename: str = "validation_rmse_comparison.png"
    validation_r2_filename: str = "validation_r2_comparison.png"
    dataset_name: str = ""
    dataset_filename: str = ""
    model_filename: str = ""
    prediction_filename: str = ""
    prediction_column: str = ""
    experiment_filename: str = "experiments.csv"
    mlflow_tracking_uri: str = ""
    mlflow_experiment_prefix: str = "ml_prediction"
    execution_log_enabled: bool = True
    experiment_enabled: bool = True
    mlflow_enabled: bool = False
    mlflow_required: bool = False
    search_enabled: bool = False

    @property
    def model_parameters(self) -> ModelParameters:
        return ModelParameters(
            n_estimators=self.n_estimators,
            n_jobs=self.n_jobs,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            max_features=self.max_features,
            bootstrap=self.bootstrap,
            random_state=self.random_state,
        )

    def audit_path(self, operation: str, run_id: str) -> Path:
        return self.audit_root / self.audit_filename_template.format(
            dataset_name=self.dataset_name,
            operation=operation,
            run_id=run_id,
        )

    def prediction_audit_path(self, run_id: str) -> Path:
        return self.audit_root / self.prediction_audit_filename_template.format(
            dataset_name=self.dataset_name,
            run_id=run_id,
        )

    def artifact_path(self, run_id: str, filename: str) -> Path:
        return self.audit_root / run_id / filename

    def experiment_path(self, run_id: str) -> Path:
        return self.audit_root / self.experiment_filename.format(
            dataset_name=self.dataset_name,
            run_id=run_id,
        )
