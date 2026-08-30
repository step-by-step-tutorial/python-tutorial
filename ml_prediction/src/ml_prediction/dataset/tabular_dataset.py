import csv
import logging
from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from ml_prediction.dataset.dataset import Dataset
from ml_prediction.features.feature_builder import FeatureBuilder

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PreparedTrainingData:
    features: pd.DataFrame
    target: pd.Series


class TabularDataset(Dataset):
    """CSV-backed dataset provider with shared tabular preparation behavior."""

    target_is_numeric = False

    def load(self) -> pd.DataFrame:
        logger.info("Loading dataset: path=%s", self.path)
        try:
            with self.path.open(newline="", encoding="utf-8") as dataset_file:
                headers = next(csv.reader(dataset_file), None)
            if headers is None:
                raise ValueError("Dataset must not be empty")
            duplicated_headers = [
                column
                for index, column in enumerate(headers)
                if column in headers[:index]
            ]
            if duplicated_headers:
                raise ValueError(f"Dataset contains duplicated column names: {duplicated_headers}")
            dataframe = pd.read_csv(self.path)
        except pd.errors.EmptyDataError as error:
            raise ValueError("Dataset must not be empty") from error
        logger.info("Dataset loaded: rows=%s columns=%s", len(dataframe), len(dataframe.columns))
        return dataframe

    def training_frame(self, target_column: str) -> pd.DataFrame:
        dataframe = self.load().copy()
        if dataframe.empty:
            raise ValueError("Dataset must not be empty")

        duplicated_columns = dataframe.columns[dataframe.columns.duplicated()].tolist()
        if duplicated_columns:
            raise ValueError(f"Dataset contains duplicated column names: {duplicated_columns}")

        if target_column not in dataframe.columns:
            raise ValueError(f"Target column '{target_column}' is missing from the dataset")

        if self.target_is_numeric:
            numeric_target = pd.to_numeric(dataframe[target_column], errors="coerce")
            if numeric_target.notna().sum() == 0:
                raise ValueError(f"Target column '{target_column}' contains no usable numeric values")
            dataframe[target_column] = numeric_target
        elif dataframe[target_column].notna().sum() == 0:
            raise ValueError(f"Target column '{target_column}' contains no usable values")
        dataframe = dataframe.dropna(subset=[target_column])
        logger.info("Prepared training frame: rows=%s target=%s", len(dataframe), target_column)
        return dataframe

    def prepare_training_data(
            self,
            target_column: str,
            feature_builder_factory: Callable[[pd.DataFrame], FeatureBuilder],
    ) -> PreparedTrainingData:
        dataframe = self.training_frame(target_column)
        target = dataframe.pop(target_column)
        features = feature_builder_factory(dataframe).build()
        logger.info(
            "Prepared training data: rows=%s features=%s target=%s",
            len(features),
            len(features.columns),
            target_column,
        )
        return PreparedTrainingData(features, target)
