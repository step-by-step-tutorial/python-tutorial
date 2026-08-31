from ml_prediction.model.trained_model import TrainedModel


class HousePriceModel(TrainedModel):

    def fit(self, features, target) -> "HousePriceModel":
        super().fit(features, target)
        return self
