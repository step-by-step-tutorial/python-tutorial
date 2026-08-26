from pathlib import Path

from test_data.config import settings as env_config


def absolute_project_path(relative_path: str | Path) -> Path:
    return (env_config.PROJECT_ROOT / relative_path).resolve()


def list_of_file_names(directory: Path) -> list[str]:
    paths = sorted(Path(directory).glob("*"))
    return [path.name for path in paths if path.is_file()]


def list_of_directory_names(directory: Path) -> list[str]:
    return sorted(path.name for path in Path(directory).glob("*") if path.is_dir())


def check_file_exists(path: Path):
    if not path.is_file():
        raise Exception(f"File {path.name} does not exist.")


def read_content_of_file(path: str) -> str:
    path = absolute_project_path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        raise Exception(f"Source file not found: {path}")
    return text


def file_to_tuple(path: str) -> tuple[str, ...]:
    content = read_content_of_file(path)
    result = tuple(line.strip() for line in content.splitlines() if line.strip())
    if not result:
        raise Exception(f"Source file is empty: {absolute_project_path(path)}")
    return result
