import logging

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from house_price_prediction.features.house_feature_model import HouseFeatureModel

logger = logging.getLogger(__name__)


class HousePriceModel:
    def __init__(self, random_state: int = 42) -> None:
        feature_model = HouseFeatureModel()
        self.pipeline = Pipeline([
            (
                "preprocessor",
                ColumnTransformer(
                    [
                        (
                            "numeric", SimpleImputer(strategy="median"),
                            list(feature_model.get_numeric_features() + feature_model.get_boolean_features()),
                        ),
                        (
                            "categorical",
                            Pipeline(
                                [
                                    ("imputer", SimpleImputer(strategy="most_frequent")),
                                    ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                                ]
                            ),
                            list(feature_model.get_categorical_features()),
                        ),
                    ]
                ),
            ),
            ("regressor", RandomForestRegressor(n_estimators=200, random_state=random_state, n_jobs=-1),),
        ])

    def fit(self, features, target) -> "HousePriceModel":
        logger.info("Training house price model: rows=%s", len(features))
        self.pipeline.fit(features, target)
        return self

    def predict(self, features):
        return self.pipeline.predict(features)
