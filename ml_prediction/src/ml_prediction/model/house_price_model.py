from ml_prediction.model.sklearn_pipeline_model import SklearnPipelineModel


class HousePriceModel(SklearnPipelineModel):
    """Backward-compatible name for the house dataset's sklearn model."""

    def fit(self, features, target) -> "HousePriceModel":
        super().fit(features, target)
        return self
