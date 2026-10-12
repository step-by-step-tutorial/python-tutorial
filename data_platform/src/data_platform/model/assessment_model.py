from dataclasses import dataclass
from typing import Any

from data_platform.model.violation_model import ViolationModel


@dataclass(frozen=True)
class AssessmentModel:
    accepted: Any
    rejected: Any
    errors: tuple[ViolationModel, ...] = ()
