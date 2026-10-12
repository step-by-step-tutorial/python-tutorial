from dataclasses import dataclass
from pathlib import Path

from ml_prediction.config.artifact_category import ArtifactCategory


@dataclass(frozen=True)
class ArtifactModel:
    path: Path
    category: ArtifactCategory
