from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from ml_prediction.features.feature_model import FeatureModel
from ml_prediction.pipeline.pipeline_builder import PipelineBuilder
from ml_prediction.pipeline.regressor_builder import RegressorBuilder


class HousePricePipelineBuilder(PipelineBuilder):
    def __init__(
            self,
            feature_model: FeatureModel,
            model_type: str,
            n_estimators: int,
            n_jobs: int,
            random_state: int,
    ) -> None:
        self._feature_model = feature_model
        self._regressor_builder = RegressorBuilder(
            model_type,
            n_estimators,
            n_jobs,
            random_state,
        )

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
