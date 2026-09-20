from abc import ABC, abstractmethod


class Metrics(ABC):
    @abstractmethod
    def to_string(self) -> str:
        raise NotImplementedError
