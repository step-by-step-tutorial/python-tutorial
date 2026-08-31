from abc import ABC, abstractmethod


class FeatureModel(ABC):
    @abstractmethod
    def get_numeric_features(self) -> tuple[str, ...]:
        raise NotImplementedError

    @abstractmethod
    def get_boolean_features(self) -> tuple[str, ...]:
        raise NotImplementedError

    @abstractmethod
    def get_categorical_features(self) -> tuple[str, ...]:
        raise NotImplementedError

    def get_feature_columns(self) -> tuple[str, ...]:
        return self.get_numeric_features() + self.get_boolean_features() + self.get_categorical_features()
