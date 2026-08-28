from abc import ABC, abstractmethod
from typing import Any


class Presenter(ABC):
    @abstractmethod
    def present(self, output: Any) -> Any:
        raise NotImplementedError
