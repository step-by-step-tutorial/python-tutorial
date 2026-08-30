from sklearn.dummy import DummyRegressor

from ml_prediction.model.model import Model


class BaselineModel(Model):
    """Mean-target reference model used only for validation comparison."""

    def __init__(self) -> None:
        self.dummy_regressor = DummyRegressor(strategy="mean")

    def fit(self, features, target) -> "BaselineModel":
        self.dummy_regressor.fit(features, target)
        return self

    def predict(self, features):
        return self.dummy_regressor.predict(features)
