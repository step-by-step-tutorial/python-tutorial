from pathlib import Path


def list_file_names(directory: Path) -> list[str]:
    return sorted(path.name for path in Path(directory).glob("*") if path.is_file())


def list_directory_names(directory: Path) -> list[str]:
    return sorted(path.name for path in Path(directory).glob("*") if path.is_dir())


def check_file_exists(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"File {path} does not exist.")


def read_lines(path: Path) -> tuple[str, ...]:
    """Return the stripped, non-blank lines of a text file."""
    content = Path(path).read_text(encoding="utf-8")
    return tuple(line.strip() for line in content.splitlines() if line.strip())
