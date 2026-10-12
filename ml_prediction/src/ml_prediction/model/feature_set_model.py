import logging
from dataclasses import dataclass

import pandas as pd

from ml_prediction.util.validation_utils import require_columns, require_not_blank, require_unique

logger = logging.getLogger(__name__)

BOOLEAN_VALUES = {True: 1, False: 0, "True": 1, "False": 0}


@dataclass(frozen=True)
class FeatureSetModel:
    numeric: tuple[str, ...]
    boolean: tuple[str, ...] = ()
    categorical: tuple[str, ...] = ()

    @property
    def columns(self) -> tuple[str, ...]:
        return self.numeric + self.boolean + self.categorical

    def extract(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        require_not_blank(dataframe, "Dataset must not be empty")
        require_unique(dataframe.columns, "Dataset contains duplicated columns")
        require_not_blank(self.columns, "No feature columns were defined")
        require_unique(self.columns, "Feature columns are duplicated")
        require_columns(dataframe, self.columns, "Dataset is missing feature columns")

        features = dataframe.loc[:, list(self.columns)].copy()
        for column in self.boolean:
            features[column] = features[column].map(BOOLEAN_VALUES)
        logger.info("Built features: rows=%s columns=%s", len(features), len(features.columns))
        return features
