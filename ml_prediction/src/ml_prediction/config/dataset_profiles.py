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
    data_lake_bucket: str
    data_lake_prefix: str


DATASET_PROFILES: dict[str, DatasetProfile] = {
    "house": DatasetProfile(
        target_column="total_price",
        task_type=TaskType.REGRESSION,
        dataset_filename="house.csv",
        model_filename="house_price_model.joblib",
        prediction_filename="house_predictions.csv",
        prediction_column="predicted_total_price",
        data_lake_bucket="house",
        data_lake_prefix="enriched/house/",
    ),
    "online_shopping": DatasetProfile(
        target_column="order_status",
        task_type=TaskType.CLASSIFICATION,
        dataset_filename="online_shopping.csv",
        model_filename="online_shopping_model.joblib",
        prediction_filename="online_shopping_predictions.csv",
        prediction_column="predicted_order_status",
        data_lake_bucket="online_shopping",
        data_lake_prefix="enriched/online_shopping/",
    ),
}
