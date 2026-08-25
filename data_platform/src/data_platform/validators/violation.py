from dataclasses import dataclass


@dataclass(frozen=True)
class Violation:
    rule: str
    message: str
