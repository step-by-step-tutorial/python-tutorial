from abc import ABC
from dataclasses import asdict, fields as dataclass_fields
from typing import Any, Self

from ml_prediction.data_model.dict_data import DictData


class AuditData(DictData, ABC):
    @classmethod
    def fields(cls) -> tuple[str, ...]:
        return tuple(field.name for field in dataclass_fields(cls))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls: type[Self], values: dict[str, Any]) -> Self:
        return cls(**values)
