from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from ml_prediction.features.feature_model import FeatureModel
from ml_prediction.pipeline.pipeline_builder import PipelineBuilder
from ml_prediction.pipeline.regressor_builder import RegressorBuilder


class TabularPipelineBuilder(PipelineBuilder):

    def __init__(self, feature_model: FeatureModel, regressor_builder: RegressorBuilder) -> None:
        self._feature_model = feature_model
        self._regressor_builder = regressor_builder

    def build(self) -> Pipeline:
        numeric_features = list(self._feature_model.get_numeric_features() + self._feature_model.get_boolean_features())
        numeric_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
        ])

        categorical_features = list(self._feature_model.get_categorical_features())
        categorical_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ])

        preprocessor = ColumnTransformer([
            ("numeric", numeric_transformer, numeric_features),
            ("categorical", categorical_transformer, categorical_features),
        ])

        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", self._regressor_builder.build()),
        ])

        return pipeline
