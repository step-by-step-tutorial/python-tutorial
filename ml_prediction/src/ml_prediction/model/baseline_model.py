from sklearn.dummy import DummyRegressor
from ml_prediction.model.model import Model

class BaselineModel(Model):
    """Mean-price reference model used only for validation comparison."""

    def __init__(self) -> None:
        self.model = DummyRegressor(strategy="mean")

    def fit(self, features, target) -> "BaselineModel":
        self.model.fit(features, target)
        return self

    def predict(self, features):
        return self.model.predict(features)
