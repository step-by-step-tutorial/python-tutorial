from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from house_price_prediction.features.feature_model import FeatureModel
from house_price_prediction.pipeline.pipeline_builder import PipelineBuilder


class HousePricePipelineBuilder(PipelineBuilder):
    def __init__(self, feature_model: FeatureModel, random_state: int) -> None:
        self._feature_model = feature_model
        self._random_state = random_state

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
                RandomForestRegressor(
                    n_estimators=200,
                    random_state=self._random_state,
                    n_jobs=-1,
                ),
            ),
        ])
