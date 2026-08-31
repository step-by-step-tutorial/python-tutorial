import logging

import pandas as pd

from ml_prediction.features.feature_model import FeatureModel
from ml_prediction.utils.data_converter import boolean_to_numeric
from ml_prediction.utils.data_validator_utils import (
    require_blank,
    require_not_blank,
    should_not_have_duplication,
)
from ml_prediction.utils.dataframe_utils import should_have_unique_columns

logger = logging.getLogger(__name__)


class FeatureBuilder:
    def __init__(self, dataframe: pd.DataFrame, feature_model: FeatureModel) -> None:
        self._dataframe = dataframe
        self._feature_model = feature_model

    def build(self) -> pd.DataFrame:
        should_have_unique_columns(self._dataframe)

        feature_columns = self._feature_model.get_feature_columns()
        require_not_blank(feature_columns, "No feature columns were defined")
        should_not_have_duplication(list(feature_columns))

        missing_columns = sorted(set(feature_columns).difference(self._dataframe.columns))
        require_blank(missing_columns,f"Feature DataFrame is missing feature columns: {missing_columns}")

        features = self._dataframe.loc[:, feature_columns].copy()
        boolean_to_numeric(features, self._feature_model.get_boolean_features())

        logger.info(f"Built features: rows={len(features)} columns={len(features.columns)}")
        return features
