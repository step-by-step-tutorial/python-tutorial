import logging

import pandas as pd

from ml_prediction.features.feature_builder import FeatureBuilder

logger = logging.getLogger(__name__)


class TabularFeatureBuilder(FeatureBuilder):
    """Build ordered feature columns from a tabular feature model."""

    require_non_empty_groups = False

    def build(self) -> pd.DataFrame:
        if self._dataframe.empty:
            raise ValueError("Feature DataFrame must not be empty")

        duplicated_columns = self._dataframe.columns[
            self._dataframe.columns.duplicated()
        ].tolist()
        if duplicated_columns:
            raise ValueError(
                f"Feature DataFrame contains duplicated column names: {duplicated_columns}"
            )

        feature_groups = (
            ("numeric", self._feature_model.get_numeric_features()),
            ("boolean", self._feature_model.get_boolean_features()),
            ("categorical", self._feature_model.get_categorical_features()),
        )
        feature_columns: list[str] = []
        boolean_columns: tuple[str, ...] = ()
        for group_name, definitions in feature_groups:
            if isinstance(definitions, str) or definitions is None:
                raise ValueError(
                    f"Invalid {group_name} feature column definitions: {definitions!r}"
                )
            try:
                definitions = tuple(definitions)
            except TypeError as error:
                raise ValueError(
                    f"Invalid {group_name} feature column definitions: {definitions!r}"
                ) from error
            if self.require_non_empty_groups and not definitions:
                raise ValueError(
                    f"Invalid {group_name} feature column definitions: no columns defined"
                )

            invalid_definitions = [
                column
                for column in definitions
                if not isinstance(column, str) or not column.strip()
            ]
            if invalid_definitions:
                raise ValueError(
                    f"Invalid {group_name} feature column definitions: {invalid_definitions}"
                )

            duplicated_definitions = [
                column
                for index, column in enumerate(definitions)
                if column in definitions[:index] or column in feature_columns
            ]
            if duplicated_definitions:
                raise ValueError(
                    f"Duplicated feature column definitions: {duplicated_definitions}"
                )

            feature_columns.extend(definitions)
            if group_name == "boolean":
                boolean_columns = definitions

        if not feature_columns:
            raise ValueError("No feature columns were defined")

        missing_columns = sorted(set(feature_columns) - set(self._dataframe.columns))
        if missing_columns:
            raise ValueError(f"Feature DataFrame is missing feature columns: {missing_columns}")

        features = self._dataframe.loc[:, feature_columns].copy()
        for column in boolean_columns:
            features[column] = features[column].map(
                {True: 1, False: 0, "True": 1, "False": 0}
            )

        logger.info(
            "Built tabular features: rows=%s columns=%s",
            len(features),
            len(features.columns),
        )
        return features
