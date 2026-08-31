import logging

import pandas as pd
from sklearn.model_selection import train_test_split

from ml_prediction.config.settings import get_settings
from ml_prediction.data_model.dataset_subset import DatasetSubset
from ml_prediction.data_model.dataset_split import DatasetSplit

logger = logging.getLogger(__name__)


class DatasetSplitter:
    def __init__(self, dataset_name: str) -> None:
        self._dataset_name = dataset_name

    def split(self, features: pd.DataFrame, target: pd.Series) -> DatasetSplit:
        settings = get_settings(self._dataset_name)
        train_features, remaining_features, train_target, remaining_target = train_test_split(
            features,
            target,
            test_size=settings.validation_size + settings.test_size,
            random_state=settings.random_state,
        )

        validation_ratio = settings.validation_size / (settings.validation_size + settings.test_size)
        validation_features, test_features, validation_target, test_target = train_test_split(
            remaining_features,
            remaining_target,
            test_size=1 - validation_ratio,
            random_state=settings.random_state,
        )

        logger.info(
            "Split dataset: train_rows=%s validation_rows=%s test_rows=%s",
            len(train_features),
            len(validation_features),
            len(test_features),
        )
        return DatasetSplit(
            train=DatasetSubset(train_features, train_target),
            validation=DatasetSubset(validation_features, validation_target),
            test=DatasetSubset(test_features, test_target),
        )
