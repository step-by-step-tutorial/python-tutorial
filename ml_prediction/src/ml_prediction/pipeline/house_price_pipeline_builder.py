from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from ml_prediction.features.house_feature_model import HouseFeatureModel
from ml_prediction.pipeline.pipeline_builder import PipelineBuilder
from ml_prediction.pipeline.regressor_builder import RegressorBuilder


class HousePricePipelineBuilder(PipelineBuilder):
    def __init__(
            self,
            feature_model: HouseFeatureModel,
            regressor_builder: RegressorBuilder,
    ) -> None:
        self._feature_model = feature_model
        self._regressor_builder = regressor_builder

    def build(self) -> Pipeline:
        return Pipeline([
            (
                "preprocessor",
                ColumnTransformer(
                    [
                        (
                            "numeric", SimpleImputer(strategy="median"),
                            list(
                                self._feature_model.get_numeric_features()
                                + self._feature_model.get_boolean_features()
                            ),
                        ),
                        (
                            "categorical",
                            Pipeline(
                                [
                                    ("imputer", SimpleImputer(strategy="most_frequent")),
                                    ("encoder", OneHotEncoder(
                                        handle_unknown="ignore",
                                        sparse_output=False,
                                    )),
                                ]
                            ),
                            list(self._feature_model.get_categorical_features()),
                        ),
                    ]
                ),
            ),
            (
                "regressor",
                self._regressor_builder.build(),
            ),
        ])
