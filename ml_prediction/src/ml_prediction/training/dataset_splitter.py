import logging

import pandas as pd
from sklearn.model_selection import train_test_split

from ml_prediction.training.training_models import DatasetPartition, DatasetPartitions

logger = logging.getLogger(__name__)


class DatasetSplitter:
    def __init__(self, validation_size: float, test_size: float, random_state: int) -> None:
        self._validation_size = validation_size
        self._test_size = test_size
        self._random_state = random_state

    def split(self, features: pd.DataFrame, target: pd.Series) -> DatasetPartitions:
        train_features, remaining_features, train_target, remaining_target = train_test_split(
            features,
            target,
            test_size=self._validation_size + self._test_size,
            random_state=self._random_state,
        )

        validation_ratio = self._validation_size / (self._validation_size + self._test_size)
        validation_features, test_features, validation_target, test_target = train_test_split(
            remaining_features,
            remaining_target,
            test_size=1 - validation_ratio,
            random_state=self._random_state,
        )

        logger.info(
            "Split dataset: train_rows=%s validation_rows=%s test_rows=%s",
            len(train_features),
            len(validation_features),
            len(test_features),
        )
        return DatasetPartitions(
            train=DatasetPartition(train_features, train_target),
            validation=DatasetPartition(validation_features, validation_target),
            test=DatasetPartition(test_features, test_target),
        )
