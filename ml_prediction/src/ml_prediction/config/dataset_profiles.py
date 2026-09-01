from ml_prediction.data_model.dataset_profile import DatasetProfile
from ml_prediction.config.settings_types import TaskType


DATASET_PROFILES: dict[str, DatasetProfile] = {
    "house": DatasetProfile(
        target_column="total_price",
        task_type=TaskType.REGRESSION,
        dataset_filename="house.csv",
        model_filename="house_price_model.joblib",
        prediction_filename="house_predictions.csv",
        prediction_column="predicted_total_price",
        experiment_filename="house_experiments.csv",
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
        experiment_filename="online_shopping_experiments.csv",
        data_lake_bucket="online_shopping",
        data_lake_prefix="enriched/online_shopping/",
    ),
}
