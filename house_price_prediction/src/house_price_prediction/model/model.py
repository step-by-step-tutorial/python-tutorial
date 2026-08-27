from abc import ABC, abstractmethod
from typing import Any


class Model(ABC):
    @abstractmethod
    def fit(self, features: Any, target: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def predict(self, features: Any) -> Any:
        raise NotImplementedError
