import os
from pathlib import Path

from ml_prediction.config.dataset_profiles import DATASET_PROFILES
from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType
from ml_prediction.data_model.app_settings import AppSettings, DatasetSource
from ml_prediction.data_model.datalake_settings import DataLakeSettings
from ml_prediction.utils.type_converter import to_bool

PROJECT_ROOT = os.getenv("PROJECT_ROOT", Path(__file__).resolve().parents[3])


def get_settings(dataset_name: str) -> AppSettings:
    profile = DATASET_PROFILES[dataset_name]

    return AppSettings(
        data_dir=Path(os.getenv("ML_PREDICTION_DATA_DIR", str(PROJECT_ROOT / "data"))),
        model_dir=Path(os.getenv("ML_PREDICTION_MODEL_DIR", str(PROJECT_ROOT / "models"))),
        target_column=os.getenv("ML_PREDICTION_TARGET_COLUMN", profile.target_column),
        validation_size=float(os.getenv("ML_PREDICTION_VALIDATION_SIZE", "0.2")),
        test_size=float(os.getenv("ML_PREDICTION_TEST_SIZE", "0.2")),
        random_state=int(os.getenv("ML_PREDICTION_RANDOM_STATE", "42")),
        data_lake=DataLakeSettings(
            endpoint=os.getenv("ML_PREDICTION_DATALAKE_ENDPOINT", "http://localhost:9000"),
            access_key=os.getenv("ML_PREDICTION_DATALAKE_ACCESS_KEY", "admin"),
            secret_key=os.getenv("ML_PREDICTION_DATALAKE_SECRET_KEY", "administrator"),
            bucket_name=os.getenv("ML_PREDICTION_DATALAKE_BUCKET_NAME", profile.data_lake_bucket),
            object_prefix=os.getenv("ML_PREDICTION_DATALAKE_PREFIX", profile.data_lake_prefix),
        ),
        task_type=ExperimentTaskType.value_of(
            os.getenv("ML_PREDICTION_TASK_TYPE", profile.task_type.value),
        ),
        model_type=os.getenv("ML_PREDICTION_MODEL_TYPE", "random_forest"),
        n_estimators=int(os.getenv("ML_PREDICTION_N_ESTIMATORS", "200")),
        n_jobs=int(os.getenv("ML_PREDICTION_N_JOBS", "-1")),
        max_depth=int(os.getenv("ML_PREDICTION_MAX_DEPTH", "0")) or None,
        min_samples_split=int(os.getenv("ML_PREDICTION_MIN_SAMPLES_SPLIT", "2")),
        min_samples_leaf=int(os.getenv("ML_PREDICTION_MIN_SAMPLES_LEAF", "1")),
        max_features=float(os.getenv("ML_PREDICTION_MAX_FEATURES", "1.0")),
        bootstrap=bool(os.getenv("ML_PREDICTION_BOOTSTRAP", "True")),
        dataset_source=DatasetSource(os.getenv("ML_PREDICTION_DATASET_SOURCE", DatasetSource.LOCAL)),
        audit_dir=Path(os.getenv("ML_PREDICTION_AUDIT_DIR", str(PROJECT_ROOT / "audit"))),
        audit_filename_template=os.getenv(
            "ML_PREDICTION_AUDIT_FILENAME_TEMPLATE",
            "{dataset_name}_{operation}_{run_id}.csv",
        ),
        prediction_audit_filename_template=os.getenv(
            "ML_PREDICTION_PREDICTION_AUDIT_FILENAME_TEMPLATE",
            "{dataset_name}_prediction_{run_id}.csv",
        ),
        comparison_dirname=os.getenv("ML_PREDICTION_COMPARISON_DIRNAME", "comparison"),
        actual_vs_predicted_filename=os.getenv(
            "ML_PREDICTION_ACTUAL_VS_PREDICTED_FILENAME", "actual_vs_predicted.png",
        ),
        residual_vs_predicted_filename=os.getenv(
            "ML_PREDICTION_RESIDUAL_VS_PREDICTED_FILENAME", "residual_vs_predicted.png",
        ),
        feature_importance_filename=os.getenv(
            "ML_PREDICTION_FEATURE_IMPORTANCE_FILENAME", "feature_importance.png",
        ),
        validation_mae_filename=os.getenv(
            "ML_PREDICTION_VALIDATION_MAE_FILENAME", "validation_mae_comparison.png",
        ),
        validation_rmse_filename=os.getenv(
            "ML_PREDICTION_VALIDATION_RMSE_FILENAME", "validation_rmse_comparison.png",
        ),
        validation_r2_filename=os.getenv(
            "ML_PREDICTION_VALIDATION_R2_FILENAME", "validation_r2_comparison.png",
        ),
        dataset_name=dataset_name,
        dataset_filename=os.getenv("ML_PREDICTION_DATASET_FILENAME", profile.dataset_filename),
        model_filename=os.getenv("ML_PREDICTION_MODEL_FILENAME", profile.model_filename),
        prediction_filename=os.getenv("ML_PREDICTION_PREDICTION_FILENAME", profile.prediction_filename),
        prediction_column=os.getenv("ML_PREDICTION_PREDICTION_COLUMN", profile.prediction_column),
        experiment_filename=os.getenv("ML_PREDICTION_EXPERIMENT_FILENAME", profile.experiment_filename),
        mlflow_tracking_uri=os.getenv("MLFLOW_TRACKING_URI", ""),
        mlflow_experiment_prefix=os.getenv("MLFLOW_EXPERIMENT_PREFIX", "ml_prediction"),
        experiment_enabled=to_bool(os.getenv("EXPERIMENT_ENABLED"), default=True),
        mlflow_enabled=to_bool(os.getenv("MLFLOW_ENABLED")),
        mlflow_required=to_bool(os.getenv("MLFLOW_REQUIRED")),
        search_enabled=to_bool(os.getenv("ML_PREDICTION_SEARCH_ENABLED")),
    )
