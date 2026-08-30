import logging

from sklearn.pipeline import Pipeline

from ml_prediction.model.model import Model
from ml_prediction.pipeline.pipeline_builder import PipelineBuilder

logger = logging.getLogger(__name__)


class SklearnPipelineModel(Model):
    """Model wrapper for a fitted sklearn preprocessing/regression pipeline."""

    def __init__(self, pipeline_builder: PipelineBuilder) -> None:
        self._pipeline = pipeline_builder.build()

    def fit(self, features, target) -> "SklearnPipelineModel":
        logger.info("Training sklearn pipeline model: rows=%s", len(features))
        self._pipeline.fit(features, target)
        return self

    def predict(self, features):
        return self._pipeline.predict(features)

    @property
    def pipeline(self) -> Pipeline:
        return self._pipeline
