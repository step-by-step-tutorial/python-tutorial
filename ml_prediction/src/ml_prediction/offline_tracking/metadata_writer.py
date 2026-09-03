import json
from pathlib import Path

from ml_prediction.offline_tracking.models import ModelMetadata


class MetadataWriter:
    def save(self, metadata: ModelMetadata, model_path: Path) -> Path:
        path = model_path.with_suffix(".metadata.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(metadata.to_dict(), indent=2), encoding="utf-8")
        return path
