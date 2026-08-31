import logging
from collections.abc import Callable
from pathlib import Path

import pandas as pd

from ml_prediction.features.feature_builder import FeatureBuilder
from ml_prediction.features.feature_model import FeatureModel
from ml_prediction.inference.predictor import Predictor
from ml_prediction.data_model.model_metadata import CURRENT_MODEL_VERSION, CURRENT_SCHEMA_VERSION, ModelMetadata
from ml_prediction.repository.local_model_repository import LocalModelRepository

logger = logging.getLogger(__name__)


class SklearnPredictor(Predictor[pd.Series]):
    """Load a persisted sklearn pipeline and predict from tabular input."""

    def __init__(
            self,
            model_path: Path,
            model_repository: LocalModelRepository,
            feature_builder_factory: Callable[[pd.DataFrame], FeatureBuilder],
            feature_model: FeatureModel,
            model_type: str,
            target_column: str,
            prediction_column: str,
    ) -> None:
        self._model_path = model_path
        self._feature_builder_factory = feature_builder_factory
        self._prediction_column = prediction_column
        try:
            metadata = model_repository.load_metadata(model_path)
        except FileNotFoundError as error:
            raise ValueError(f"Persisted model metadata is missing for '{model_path}'") from error
        self._validate_metadata(metadata, feature_model, model_type, target_column)
        self.pipeline = model_repository.load(model_path)

    @property
    def model_path(self) -> Path:
        return self._model_path

    @property
    def prediction_column(self) -> str:
        return self._prediction_column

    def predict(self, dataframe: pd.DataFrame) -> pd.Series:
        features = self._feature_builder_factory(dataframe).build()
        predictions = self.pipeline.predict(features)
        logger.info(
            "Generated predictions: rows=%s prediction_column=%s",
            len(predictions),
            self._prediction_column,
        )
        return pd.Series(predictions, index=dataframe.index, name=self._prediction_column)

    @staticmethod
    def _validate_metadata(
            metadata: ModelMetadata,
            feature_model: FeatureModel,
            model_type: str,
            target_column: str,
    ) -> None:
        if metadata.model_type != model_type:
            raise ValueError(
                f"Persisted model type '{metadata.model_type}' is incompatible with current model type '{model_type}'"
            )
        if metadata.target_column != target_column:
            raise ValueError(
                f"Persisted model target column '{metadata.target_column}' is incompatible with "
                f"current target column '{target_column}'"
            )
        if metadata.schema_version != CURRENT_SCHEMA_VERSION:
            raise ValueError(
                f"Persisted model schema version '{metadata.schema_version}' is incompatible with "
                f"current schema version '{CURRENT_SCHEMA_VERSION}'"
            )
        if metadata.model_version != CURRENT_MODEL_VERSION:
            raise ValueError(
                f"Persisted model version '{metadata.model_version}' is incompatible with "
                f"current model version '{CURRENT_MODEL_VERSION}'"
            )

        saved_features = (
                metadata.numeric_features
                + metadata.boolean_features
                + metadata.categorical_features
        )
        duplicated_saved_features = sorted(
            {column for column in saved_features if saved_features.count(column) > 1}
        )
        if duplicated_saved_features:
            raise ValueError(
                "Persisted model feature schema contains duplicated feature columns: "
                f"{duplicated_saved_features}"
            )
        current_features = feature_model.get_feature_columns()
        missing_from_current = sorted(set(saved_features) - set(current_features))
        missing_from_saved = sorted(set(current_features) - set(saved_features))
        if missing_from_current or missing_from_saved:
            raise ValueError(
                "Persisted model feature schema is incompatible with the current schema: "
                f"missing from current={missing_from_current}, missing from persisted={missing_from_saved}"
            )
