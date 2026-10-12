from dataclasses import dataclass
from pathlib import Path
from typing import Any

from geodata_pipeline.util.file_utils import read_json, resolve_path
from geodata_pipeline.util.text_utils import normalize


@dataclass(frozen=True)
class Target:
    country_code: str
    country: str
    state_code: str
    state: str
    cities: frozenset[str]
    input_file: Path
    output_file: Path

    @classmethod
    def from_dict(cls, raw: dict[str, Any], base_dir: Path, output_dir: Path) -> "Target":
        return cls(
            country_code=raw["country_code"],
            country=raw["country"],
            state_code=raw["state_code"],
            state=raw["state"],
            cities=frozenset(normalize(city) for city in raw["cities"]),
            input_file=resolve_path(base_dir, raw["input_file"]),
            output_file=output_dir / raw["output_file"],
        )

    @property
    def state_key(self) -> tuple[str, str]:
        return self.country_code, self.state_code

    def is_state(self, value: str) -> bool:
        return normalize(value) in {normalize(self.state), normalize(self.state_code)}

    def is_city(self, city: str | None) -> bool:
        return bool(city) and normalize(city) in self.cities


@dataclass(frozen=True)
class PipelineConfig:
    geonames_file: Path
    postal_codes_file: Path
    output_dir: Path
    targets: tuple[Target, ...]

    @classmethod
    def from_file(cls, config_file: Path) -> "PipelineConfig":
        """Load the config; relative paths are resolved against the config file's directory."""
        base_dir = config_file.resolve().parent
        raw = read_json(config_file)
        output_dir = resolve_path(base_dir, raw["output_dir"])

        return cls(
            geonames_file=resolve_path(base_dir, raw["geonames_file"]),
            postal_codes_file=resolve_path(base_dir, raw["postal_codes_file"]),
            output_dir=output_dir,
            targets=tuple(Target.from_dict(item, base_dir, output_dir) for item in raw["targets"]),
        )

    @property
    def source_files(self) -> tuple[Path, ...]:
        return self.geonames_file, self.postal_codes_file
