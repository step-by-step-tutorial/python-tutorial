import logging

import pandas as pd

from house_price_prediction.features.feature_builder import FeatureBuilder
from house_price_prediction.utils.collection_utils import check_equal

logger = logging.getLogger(__name__)


class HouseFeatureBuilder(FeatureBuilder):
    def build(self) -> pd.DataFrame:
        feature_columns = self._feature_model.get_feature_columns()
        check_equal(feature_columns, self._dataframe.columns)

        features = self._dataframe.loc[:, feature_columns].copy()
        for column in self._feature_model.get_boolean_features():
            features[column] = features[column].map({True: 1, False: 0, "True": 1, "False": 0})

        logger.info(f"Built house features: rows={len(features)} columns={len(features.columns)}")
        return features
