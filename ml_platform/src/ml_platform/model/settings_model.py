import os
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ml_platform.config.dataset_source import DatasetSource
from ml_platform.config.model_type import ModelType
from ml_platform.config.operation import Operation
from ml_platform.config.task_type import TaskType
from ml_platform.model.dataset_profile_model import DatasetProfileModel
from ml_platform.util.type_utils import to_bool, to_optional_int

DEFAULT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class DataLakeSettingsModel:
    endpoint: str
    access_key: str
    secret_key: str
    bucket_name: str
    object_prefix: str

    @classmethod
    def from_env(cls, environ: Mapping[str, str], profile: DatasetProfileModel) -> "DataLakeSettingsModel":
        return cls(
            endpoint=environ.get("ML_PLATFORM_DATALAKE_ENDPOINT", "http://localhost:9000"),
            access_key=environ.get("ML_PLATFORM_DATALAKE_ACCESS_KEY", "admin"),
            secret_key=environ.get("ML_PLATFORM_DATALAKE_SECRET_KEY", "administrator"),
            bucket_name=profile.data_lake_bucket,
            object_prefix=profile.data_lake_prefix,
        )


@dataclass(frozen=True)
class ModelParametersModel:
    n_estimators: int = 200
    n_jobs: int = -1
    max_depth: int | None = None
    min_samples_split: int = 2
    min_samples_leaf: int = 1
    max_features: float = 1.0
    bootstrap: bool = True
    random_state: int = 42

    @classmethod
    def from_env(cls, environ: Mapping[str, str], random_state: int) -> "ModelParametersModel":
        return cls(
            n_estimators=int(environ.get("ML_PLATFORM_N_ESTIMATORS", "200")),
            n_jobs=int(environ.get("ML_PLATFORM_N_JOBS", "-1")),
            max_depth=to_optional_int(environ.get("ML_PLATFORM_MAX_DEPTH")),
            min_samples_split=int(environ.get("ML_PLATFORM_MIN_SAMPLES_SPLIT", "2")),
            min_samples_leaf=int(environ.get("ML_PLATFORM_MIN_SAMPLES_LEAF", "1")),
            max_features=float(environ.get("ML_PLATFORM_MAX_FEATURES", "1.0")),
            bootstrap=to_bool(environ.get("ML_PLATFORM_BOOTSTRAP"), default=True),
            random_state=random_state,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MlflowSettingsModel:
    enabled: bool = False
    tracking_uri: str = ""
    experiment_prefix: str = "ml_platform"

    @classmethod
    def from_env(cls, environ: Mapping[str, str]) -> "MlflowSettingsModel":
        return cls(
            enabled=to_bool(environ.get("MLFLOW_ENABLED")),
            tracking_uri=environ.get("MLFLOW_TRACKING_URI", ""),
            experiment_prefix=environ.get("MLFLOW_EXPERIMENT_PREFIX", "ml_platform"),
        )


@dataclass(frozen=True)
class SettingsModel:
    profile: DatasetProfileModel
    data_dir: Path
    model_dir: Path
    audit_dir: Path
    output_dir: Path
    data_lake: DataLakeSettingsModel
    dataset_source: DatasetSource = DatasetSource.LOCAL
    validation_size: float = 0.2
    test_size: float = 0.2
    random_state: int = 42
    model_type: ModelType = ModelType.RANDOM_FOREST
    model_parameters: ModelParametersModel = ModelParametersModel()
    search_enabled: bool = False
    execution_log_enabled: bool = True
    experiment_enabled: bool = True
    mlflow: MlflowSettingsModel = MlflowSettingsModel()

    @classmethod
    def from_env(
            cls,
            profile: DatasetProfileModel,
            search_enabled: bool = False,
            environ: Mapping[str, str] | None = None,
    ) -> "SettingsModel":
        environ = os.environ if environ is None else environ
        root = Path(environ.get("PROJECT_ROOT", DEFAULT_ROOT))
        random_state = int(environ.get("ML_PLATFORM_RANDOM_STATE", "42"))
        return cls(
            profile=profile,
            data_dir=Path(environ.get("ML_PLATFORM_DATA_DIR", root / "data")),
            model_dir=Path(environ.get("ML_PLATFORM_MODEL_DIR", root / "models")),
            audit_dir=Path(environ.get("ML_PLATFORM_AUDIT_DIR", root / "audit_log")),
            output_dir=Path(environ.get("ML_PLATFORM_OUTPUT_DIR", root / "output")),
            data_lake=DataLakeSettingsModel.from_env(environ, profile),
            dataset_source=DatasetSource(environ.get("ML_PLATFORM_DATASET_SOURCE", DatasetSource.LOCAL)),
            validation_size=float(environ.get("ML_PLATFORM_VALIDATION_SIZE", "0.2")),
            test_size=float(environ.get("ML_PLATFORM_TEST_SIZE", "0.2")),
            random_state=random_state,
            model_type=ModelType(environ.get("ML_PLATFORM_MODEL_TYPE", ModelType.RANDOM_FOREST)),
            model_parameters=ModelParametersModel.from_env(environ, random_state),
            search_enabled=search_enabled or to_bool(environ.get("ML_PLATFORM_SEARCH_ENABLED")),
            execution_log_enabled=to_bool(environ.get("EXECUTION_LOG_ENABLED"), default=True),
            experiment_enabled=to_bool(environ.get("EXPERIMENT_ENABLED"), default=True),
            mlflow=MlflowSettingsModel.from_env(environ),
        )

    @property
    def dataset_name(self) -> str:
        return self.profile.name

    @property
    def task_type(self) -> TaskType:
        return self.profile.task_type

    @property
    def dataset_path(self) -> Path:
        return self.data_dir / f"{self.dataset_name}.csv"

    @property
    def model_path(self) -> Path:
        return self.model_dir / f"{self.dataset_name}_model.joblib"

    @property
    def prediction_path(self) -> Path:
        return self.output_dir / f"{self.dataset_name}_predictions.csv"

    @property
    def experiment_path(self) -> Path:
        return self.audit_dir / f"{self.dataset_name}_experiments.csv"

    def execution_log_path(self, operation: Operation, run_id: str) -> Path:
        return self.audit_dir / f"{self.dataset_name}_{operation}_{run_id}.csv"

    def artifact_path(self, run_id: str, file_name: str) -> Path:
        return self.audit_dir / run_id / file_name

    def comparison_path(self, file_name: str) -> Path:
        return self.audit_dir / "comparison" / f"{self.dataset_name}_{file_name}"
