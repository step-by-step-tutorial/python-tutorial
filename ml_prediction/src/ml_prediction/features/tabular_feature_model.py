import pandas as pd

from ml_prediction.features.feature_model import FeatureModel


class TabularFeatureModel(FeatureModel):
    """Feature groups inferred from a prepared tabular DataFrame."""

    def __init__(self, dataframe: pd.DataFrame) -> None:
        self._numeric_features = tuple(dataframe.select_dtypes(include="number").columns)
        self._boolean_features = tuple(dataframe.select_dtypes(include="bool").columns)
        known_features = set(self._numeric_features) | set(self._boolean_features)
        self._categorical_features = tuple(
            column for column in dataframe.columns if column not in known_features
        )

    def get_numeric_features(self) -> tuple[str, ...]:
        return self._numeric_features

    def get_boolean_features(self) -> tuple[str, ...]:
        return self._boolean_features

    def get_categorical_features(self) -> tuple[str, ...]:
        return self._categorical_features
