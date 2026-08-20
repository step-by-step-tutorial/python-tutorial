import json
from pathlib import Path
from typing import Any

import env_config


def list_of_file_names(directory: Path) -> list[str]:
    paths = sorted(Path(directory).glob("*"))
    return [path.name for path in paths]


def read_json_file(path: Path) -> dict[str, Any]:
    file_path = Path(path)
    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as error:
        raise Exception(f"Reading JSON file ({file_path}) failed due to: {error}")

    return raw


def output_file_path(output_file: str) -> Path:
    return env_config.OUTPUT_DIR / output_file


def relative_to_project_root(path: Path) -> str:
    try:
        return path.relative_to(env_config.PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()
