from abc import ABC
from dataclasses import fields as dataclass_fields

from ml_prediction.data_model.dictionary import Dictionary


class AuditData(Dictionary, ABC):
    @classmethod
    def fields(cls) -> tuple[str, ...]:
        return tuple(field.name for field in dataclass_fields(cls))
