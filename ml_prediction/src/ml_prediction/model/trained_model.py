import logging

from sklearn.pipeline import Pipeline

from ml_prediction.model.model import Model
from ml_prediction.pipeline.pipeline_builder import PipelineBuilder

logger = logging.getLogger(__name__)


class TrainedModel(Model):

    def __init__(self, builder: PipelineBuilder) -> None:
        self._pipeline = builder.build()

    def fit(self, features, target) -> "TrainedModel":
        logger.info(f"Training sklearn pipeline model: rows={len(features)}")
        self._pipeline.fit(features, target)
        return self

    def predict(self, features):
        return self._pipeline.predict(features)

    @property
    def pipeline(self) -> Pipeline:
        return self._pipeline
