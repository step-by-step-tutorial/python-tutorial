from dataclasses import dataclass


@dataclass(frozen=True)
class ViolationModel:
    rule: str
    message: str
