import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from geodata_pipeline.text import normalize


@dataclass(frozen=True)
class Target:
    country_code: str
    country: str
    state_code: str
    state: str
    cities: frozenset[str]
    input_file: Path
    output_file: Path


@dataclass(frozen=True)
class PipelineConfig:
    geonames_file: Path
    postal_codes_file: Path
    output_dir: Path
    targets: tuple[Target, ...]


def load_config(config_file: Path) -> PipelineConfig:
    """Load the pipeline config; relative paths are resolved against the config file's directory."""
    base_dir = config_file.resolve().parent
    with config_file.open("r", encoding="utf-8") as file:
        raw = json.load(file)

    output_dir = _resolve(base_dir, raw["output_dir"])
    return PipelineConfig(
        geonames_file=_resolve(base_dir, raw["geonames_file"]),
        postal_codes_file=_resolve(base_dir, raw["postal_codes_file"]),
        output_dir=output_dir,
        targets=tuple(_to_target(item, base_dir, output_dir) for item in raw["targets"]),
    )


def _to_target(raw: dict[str, Any], base_dir: Path, output_dir: Path) -> Target:
    return Target(
        country_code=raw["country_code"],
        country=raw["country"],
        state_code=raw["state_code"],
        state=raw["state"],
        cities=frozenset(normalize(city) for city in raw["cities"]),
        input_file=_resolve(base_dir, raw["input_file"]),
        output_file=output_dir / raw["output_file"],
    )


def _resolve(base_dir: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (base_dir / path).resolve()
