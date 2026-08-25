from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ValidationError:
    rule: str
    message: str
    row_id: Any = None


@dataclass(frozen=True)
class ValidationResult:
    valid: Any
    invalid: Any
    errors: tuple[ValidationError, ...] = ()


class Validator(Protocol):
    def validate(self, dataframe: Any) -> ValidationResult:
        ...
