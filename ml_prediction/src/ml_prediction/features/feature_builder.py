import logging

import pandas as pd

from ml_prediction.features.feature_model import FeatureModel
from ml_prediction.utils.data_converter import boolean_to_numeric
from ml_prediction.utils.data_validator_utils import (
    require_not_blank,
    should_be_same,
    should_not_have_duplication,
)
from ml_prediction.utils.dataframe_utils import extract, should_have_unique_columns

logger = logging.getLogger(__name__)


class FeatureBuilder:
    def __init__(self, dataframe: pd.DataFrame, model: FeatureModel) -> None:
        self._dataframe = dataframe
        self._dataframe_columns = self._dataframe.columns
        self._model = model
        self._feature_columns = self._model.get_feature_columns()
        self._boolean_features = self._model.get_boolean_features()

    def build(self) -> pd.DataFrame:
        should_have_unique_columns(self._dataframe)
        require_not_blank(self._feature_columns, "No feature columns were defined")
        should_not_have_duplication(list(self._feature_columns))
        should_be_same(
            first=self._feature_columns,
            second=self._dataframe_columns,
            error_message="Feature DataFrame is missing feature columns: {difference}",
        )

        features = extract(self._dataframe, self._feature_columns)
        boolean_to_numeric(features, self._boolean_features)

        logger.info(f"Built features: rows={len(features)} columns={len(features.columns)}")
        return features
