import hashlib
from pathlib import Path
from uuid import uuid4


class IdGenerator:
    @staticmethod
    def generate() -> str:
        return str(uuid4())

    @staticmethod
    def model_id(model_path: Path | None) -> str:
        if not isinstance(model_path, Path) or not model_path.exists():
            return ""
        digest = hashlib.sha256()
        with model_path.open("rb") as model_file:
            for chunk in iter(lambda: model_file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
