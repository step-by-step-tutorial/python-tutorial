from abc import ABC, abstractmethod
from typing import Any


class View(ABC):
    @abstractmethod
    def render(self, data: Any) -> Any:
        raise NotImplementedError
