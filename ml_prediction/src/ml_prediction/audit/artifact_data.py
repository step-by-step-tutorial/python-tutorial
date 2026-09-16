from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ArtifactData:
    path: Path
    category: str


__all__ = ["ArtifactData"]
