from abc import ABC, abstractmethod
from typing import Any


class Visualizer(ABC):
    @abstractmethod
    def render(self, dto: Any) -> Any:
        raise NotImplementedError
