from pathlib import Path

import env_config


def absolute_project_path(relative_path: str | Path) -> Path:
    return (env_config.PROJECT_ROOT / relative_path).resolve()


def list_of_file_names(directory: Path) -> list[str]:
    paths = sorted(Path(directory).glob("*"))
    return [path.name for path in paths]


def check_file_exists(path: Path):
    if not path.is_file():
        raise Exception(f"File {path.name} does not exist.")
