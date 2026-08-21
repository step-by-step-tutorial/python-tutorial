from pathlib import Path


FORMAT_DETAILS: dict[str, tuple[str, str]] = {
    "csv": ("csv", "text/csv"),
    "json": ("json", "application/json"),
    "xml": ("xml", "application/xml"),
}


def output_file_name(output_file: str, format_name: str) -> Path:
    extension, _ = FORMAT_DETAILS[format_name]
    return Path(output_file).with_suffix(f".{extension}")


def media_type_for(format_name: str) -> str:
    return FORMAT_DETAILS[format_name][1]
