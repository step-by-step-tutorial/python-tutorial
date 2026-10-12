import logging
from dataclasses import dataclass

import pandas as pd
from sklearn.model_selection import train_test_split

from ml_prediction.model.feature_set_model import FeatureSetModel

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FeaturesAndTargetModel:
    features: pd.DataFrame
    target: pd.Series

    @classmethod
    def from_dataframe(
            cls,
            dataframe: pd.DataFrame,
            target_column: str,
            feature_set: FeatureSetModel,
    ) -> "FeaturesAndTargetModel":
        dataframe = dataframe.dropna(subset=[target_column]).copy()
        target = dataframe.pop(target_column)
        return cls(feature_set.extract(dataframe), target)

    def __len__(self) -> int:
        return len(self.features)


@dataclass(frozen=True)
class DatasetSplitModel:
    train: FeaturesAndTargetModel
    validation: FeaturesAndTargetModel
    test: FeaturesAndTargetModel

    @classmethod
    def from_features(
            cls,
            data: FeaturesAndTargetModel,
            validation_size: float,
            test_size: float,
            random_state: int,
    ) -> "DatasetSplitModel":
        holdout_size = validation_size + test_size
        train_features, holdout_features, train_target, holdout_target = train_test_split(
            data.features, data.target, test_size=holdout_size, random_state=random_state,
        )
        validation_features, test_features, validation_target, test_target = train_test_split(
            holdout_features, holdout_target, test_size=1 - validation_size / holdout_size, random_state=random_state,
        )
        split = cls(
            train=FeaturesAndTargetModel(train_features, train_target),
            validation=FeaturesAndTargetModel(validation_features, validation_target),
            test=FeaturesAndTargetModel(test_features, test_target),
        )
        logger.info("Split dataset: train=%s validation=%s test=%s", len(split.train), len(split.validation),
                    len(split.test))
        return split
