from dataclasses import dataclass
from typing import Any

from data_platform.validators.violation import Violation


@dataclass(frozen=True)
class Assessment:
    accepted: Any
    rejected: Any
    errors: tuple[Violation, ...] = ()
