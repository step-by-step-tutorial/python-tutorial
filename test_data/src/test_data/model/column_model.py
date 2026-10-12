from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ColumnModel:
    name: str
    type: str
    file: str | None = None
    method: str | None = None
    formula: str | None = None
    domain: str | None = None
    value: str | None = None
    start: int | None = None
    step: int | None = None
    min: int | None = None
    max: int | None = None
    min_field: str | None = None
    max_field: str | None = None
    date_start: str | None = None
    date_end: str | None = None
    source_field: str | None = None
    source_fields: tuple[str, ...] | None = None
    mapping_file: str | None = None
    file_template: str | None = None
    key_column: str | None = None
    value_column: str | None = None
    value_template: str | None = None
    required_columns: tuple[str, ...] | None = None
    candidate_limit: int | None = None
    filter_column: str | None = None
    filter_values: tuple[str, ...] | None = None
    filter_fallback_values: tuple[str, ...] | None = None
    exclude_directories: tuple[str, ...] | None = None
    file_column: str | None = None
    file_columns: tuple[str, ...] | None = None
    separator: str | None = None
    present_when: str | None = None
    nullable: bool = False
    null_probability: float | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ColumnModel":
        """Build a column from its JSON config; JSON lists become tuples so the model stays hashable."""
        data = {key: tuple(value) if isinstance(value, list) else value for key, value in raw.items()}
        return cls(**data)
