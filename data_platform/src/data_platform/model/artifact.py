from dataclasses import dataclass


@dataclass(frozen=True)
class Artifact:
    storage: str
    path: str

