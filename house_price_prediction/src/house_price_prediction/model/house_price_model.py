import logging
from pathlib import Path

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from house_price_prediction.features.house_features import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
)

logger = logging.getLogger(__name__)


class HousePriceModel:
    def __init__(self, random_state: int = 42) -> None:
        numeric_pipeline = Pipeline([("imputer", SimpleImputer(strategy="median"))])
        categorical_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ])
        preprocessor = ColumnTransformer([
            ("numeric", numeric_pipeline, list(NUMERIC_FEATURES)),
            ("categorical", categorical_pipeline, list(CATEGORICAL_FEATURES)),
        ])
        self.pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor(
                n_estimators=200,
                random_state=random_state,
                n_jobs=-1,
            )),
        ])

    def fit(self, features, target) -> "HousePriceModel":
        logger.info("Training house price model: rows=%s", len(features))
        self.pipeline.fit(features, target)
        return self

    def predict(self, features):
        return self.pipeline.predict(features)

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)
        logger.info("Saved house price model: path=%s", path)
        return path

    @classmethod
    def load(cls, path: Path) -> "HousePriceModel":
        logger.info("Loading house price model: path=%s", path)
        return joblib.load(path)
