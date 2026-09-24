from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Any, Self


class Dictionary(ABC):
    @classmethod
    def from_dict(cls: type[Self], values: dict[str, Any]) -> Self:
        return cls(**values)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
