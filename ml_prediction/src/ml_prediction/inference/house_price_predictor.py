from ml_prediction.features.house_feature_model import HouseFeatureModel
from ml_prediction.inference.sklearn_predictor import SklearnPredictor
from ml_prediction.repository.local_model_repository import LocalModelRepository


class HousePricePredictor(SklearnPredictor):
    def __init__(
            self,
            model_path,
            model_repository: LocalModelRepository,
            feature_builder_factory,
            feature_model: HouseFeatureModel,
            model_type: str,
            target_column: str,
            prediction_column: str = "predicted_total_price",
    ) -> None:
        super().__init__(
            model_path,
            model_repository,
            feature_builder_factory,
            feature_model,
            model_type,
            target_column,
            prediction_column=prediction_column,
        )
