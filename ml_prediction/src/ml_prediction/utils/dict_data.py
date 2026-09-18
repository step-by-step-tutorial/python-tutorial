from abc import ABC, abstractmethod
from typing import Any


class DictData(ABC):
    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Return the serializable row representation of this data."""
