from sklearn.dummy import DummyRegressor


class BaselineModel:
    def __init__(self) -> None:
        self.model = DummyRegressor(strategy="mean")

    def fit(self, features, target) -> "BaselineModel":
        self.model.fit(features, target)
        return self

    def predict(self, features):
        return self.model.predict(features)
