import ast
from abc import ABC, abstractmethod
from datetime import date
from math import prod
from random import Random
from typing import Mapping

from test_data.config import settings as env_config
from test_data.repository.source_repository import SourceRepository
from test_data.model import ColumnModel
from test_data.util.date_utils import days_between, random_date_between, random_date_from
from test_data.util.file_utils import list_directory_names
from test_data.util.formula_utils import check_formula, evaluate_formula
from test_data.util.text_utils import to_email_local_part
from test_data.util.validation_utils import (
    check_min_max,
    require_blank,
    require_not_blank,
    require_or_default,
    require_or_raise_map,
    require_iso_date,
    require_xor,
    should_not_be_negative,
)

Row = Mapping[str, str]
SOURCE_REPOSITORY = SourceRepository()

DEFAULT_MIN_OFFSET_DAYS = 1
DEFAULT_MAX_OFFSET_DAYS = 7
DEFAULT_NULL_PROBABILITY = 0.2


class ColumnGenerator(ABC):

    def __init__(self, model: ColumnModel) -> None:
        self.model = model
        self.source_repository = SOURCE_REPOSITORY
        self.rand = Random(self.seed)
        self.validate()

    @property
    def seed(self) -> str:
        # One random stream per column: a shared seed would make columns of the same shape move together.
        return f"{env_config.RANDOM_SEED}:{self.model.name}"

    @property
    def dependencies(self) -> tuple[str, ...]:
        return ()

    @abstractmethod
    def generate(self, row: Row, row_index: int) -> str:
        pass

    def validate(self) -> None:
        pass

    def require(self, *keys: str) -> None:
        missing = [key for key in keys if getattr(self.model, key) is None]
        require_blank(missing,
                      error_message=f"Column {self.model.name} of type {self.model.type} requires: {', '.join(missing)}.")

    def get_by_source(self, row: Row) -> str:
        source_field = require_not_blank(self.model.source_field)
        return require_not_blank(row.get(source_field),
                                 f"Column {self.model.name} depends on source field {source_field}.")

    def get_by_key(self, mapping: Mapping[str, str], key: str) -> str:
        return require_or_raise_map(mapping, key, f"'{key}' not found in mapping for column {self.model.name}.")


class SequenceColumn(ColumnGenerator):

    def generate(self, row: Row, row_index: int) -> str:
        return str(require_or_default(self.model.start, 1) + row_index * require_or_default(self.model.step, 1))


class FixedColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("value")

    def generate(self, row: Row, row_index: int) -> str:
        return str(require_not_blank(self.model.value))


class RandomIntColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("min", "max")
        check_min_max(
            minimum=self.model.min,
            maximum=self.model.max,
            error_message=f"Column {self.model.name}: 'min' must not be greater than 'max'."
        )

    def generate(self, row: Row, row_index: int) -> str:
        return str(self.rand.randint(self.model.min, self.model.max))  # type: ignore[arg-type]


class RandomFloatColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("min", "max")
        check_min_max(
            minimum=self.model.min,
            maximum=self.model.max,
            error_message=f"Column {self.model.name}: 'min' must not be greater than 'max'.",
        )

    def generate(self, row: Row, row_index: int) -> str:
        return f"{self.rand.uniform(self.model.min, self.model.max):.6f}"  # type: ignore[arg-type]


class RandomBooleanColumn(ColumnGenerator):

    def generate(self, row: Row, row_index: int) -> str:
        return str(self.rand.choice((True, False)))


class RandomTimestampColumn(ColumnGenerator):

    def __init__(self, model: ColumnModel):
        self.start = None
        self.end = None
        super().__init__(model)

    def validate(self) -> None:
        self.require("date_start", "date_end")
        self.start = require_iso_date(self.model.date_start)
        self.end = require_iso_date(self.model.date_end)
        days_between(
            require_not_blank(self.start),
            require_not_blank(self.end),
            error_message=f"date_start must be earlier than or equal to date_end: {self.model.name}",
        )

    def generate(self, row: Row, row_index: int) -> str:
        day = random_date_between(self.start, self.end, self.rand)
        hour = self.rand.randrange(24)
        minute = self.rand.randrange(60)
        second = self.rand.randrange(60)
        return f"{day}T{hour:02d}:{minute:02d}:{second:02d}"


class RandomDateColumn(ColumnGenerator):

    def __init__(self, model: ColumnModel):
        self.start = None
        self.end = None
        super().__init__(model)

    def validate(self) -> None:
        self.require("date_start", "date_end")
        self.start = require_iso_date(self.model.date_start)
        self.end = require_iso_date(self.model.date_end)
        days_between(
            require_not_blank(self.start),
            require_not_blank(self.end),
            error_message=f"date_start must be earlier than or equal to date_end: {self.model.name}",
        )

    def generate(self, row: Row, row_index: int) -> str:
        return random_date_between(self.start, self.end, self.rand)


class RandomFromFileColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("file")

    def generate(self, row: Row, row_index: int) -> str:
        return self.rand.choice(self.source_repository.read_text_file(self.model.file))  # type: ignore[arg-type]


class RandomFromDirectoryColumn(ColumnGenerator):
    def validate(self) -> None:
        self.require("file")

    def generate(self, row: Row, row_index: int) -> str:
        directories = list_directory_names(env_config.project_path(require_not_blank(self.model.file)))
        excluded = set(self.model.exclude_directories or ())
        directories = [directory for directory in directories if directory not in excluded]
        if not directories:
            raise ValueError(f"No directories found for column {self.model.name}.")
        return self.rand.choice(directories)


class RandomFromMappedFileColumn(ColumnGenerator):

    def __init__(self, model: ColumnModel):
        self.file_columns = None
        self.separator = None
        super().__init__(model)

    def validate(self) -> None:
        self.require("source_field", "mapping_file", "key_column")
        require_xor(
            obj1=self.model.file_column,
            obj2=self.model.file_columns,
            error_message=f"Column {self.model.name} of type {self.model.type} requires: XOR of file_column and file_columns."
        )

        self.file_columns = require_or_default(obj=self.model.file_columns, default=(self.model.file_column,))
        self.separator = require_or_default(obj=self.model.separator, default=" ")

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (require_not_blank(self.model.source_field),)

    def generate(self, row: Row, row_index: int) -> str:
        key = self.get_by_source(row)
        parts: list[str] = []
        for value_column in self.file_columns:
            mapping = self.source_repository.read_csv_file(
                require_not_blank(self.model.mapping_file),
                require_not_blank(self.model.key_column),
                value_column
            )
            source_file = self.get_by_key(mapping, key)
            parts.append(self.rand.choice(self.source_repository.read_text_file(source_file)))

        return self.separator.join(parts)


class RandomFromMappedCsvColumn(ColumnGenerator):
    _candidate_rows: dict[tuple[object, ...], tuple[Mapping[str, str], ...]] = {}
    _selected_rows: dict[tuple[object, ...], Mapping[str, str]] = {}

    def validate(self) -> None:
        self.require("source_field", "key_column")
        require_xor(
            obj1=self.model.value_column,
            obj2=self.model.value_template,
            error_message=f"Column {self.model.name} requires exactly one of value_column or value_template."
        )
        require_xor(
            obj1=self.model.mapping_file,
            obj2=self.model.file_template,
            error_message=f"Column {self.model.name} requires exactly one of mapping_file or file_template."
        )

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (require_not_blank(self.model.source_field),)

    def generate(self, row: Row, row_index: int) -> str:
        source_value = self.get_by_source(row)
        mapping_file = self.model.mapping_file
        if self.model.file_template is not None:
            source_field = require_not_blank(self.model.source_field)
            mapping_file = self.model.file_template.format(**{source_field: source_value})
        mapping_file = require_not_blank(mapping_file)
        key_column = require_not_blank(self.model.key_column)
        candidate_cache_key = (
            mapping_file,
            source_value,
            key_column,
            self.model.filter_column,
            tuple(self.model.filter_values or ()),
            tuple(self.model.filter_fallback_values or ()),
            tuple(self.model.required_columns or ()),
            self.model.candidate_limit,
        )
        selected_cache_key = candidate_cache_key + (row_index,)
        selected = self._selected_rows.get(selected_cache_key)
        if selected is None:
            rows = self._candidate_rows.get(candidate_cache_key)
            if rows is None:
                rows = self.source_repository.read_csv_rows(
                    mapping_file,
                    key_column,
                    source_value,
                    self.model.candidate_limit,
                )
                if self.model.filter_column and self.model.filter_values:
                    filtered_rows = tuple(
                        row for row in rows if row.get(self.model.filter_column) in self.model.filter_values
                    )
                    if not filtered_rows and self.model.filter_fallback_values:
                        filtered_rows = tuple(
                            row
                            for row in rows
                            if row.get(self.model.filter_column) in self.model.filter_fallback_values
                        )
                    rows = filtered_rows
                if self.model.required_columns:
                    rows = tuple(
                        row
                        for row in rows
                        if all(row.get(column) for column in self.model.required_columns)
                    )
                self._candidate_rows[candidate_cache_key] = rows
            if not rows:
                raise ValueError(f"No rows found for '{source_value}' in mapping for column {self.model.name}.")
            selected = self.rand.choice(rows)
            self._selected_rows[selected_cache_key] = selected
        if self.model.value_template is not None:
            try:
                return self.model.value_template.format_map(selected)
            except (KeyError, ValueError) as error:
                raise ValueError(f"Column {self.model.name} has an invalid value template.") from error

        return require_or_raise_map(
            selected,
            require_not_blank(self.model.value_column),
            f"Column {self.model.name} has no value in the selected address record.",
        )


class LookupFromCsvColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("source_field", "mapping_file", "key_column", "value_column")

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (require_not_blank(self.model.source_field),)

    def generate(self, row: Row, row_index: int) -> str:
        mapping = self.source_repository.read_csv_file(
            require_not_blank(self.model.mapping_file),
            require_not_blank(self.model.key_column),
            require_not_blank(self.model.value_column),
        )
        return self.get_by_key(mapping, self.get_by_source(row))


class ProductColumn(ColumnGenerator):

    def __init__(self, model: ColumnModel) -> None:
        self._source_fields: tuple[str, ...] = ()
        super().__init__(model)

    def validate(self) -> None:
        self.require("source_fields")
        self._source_fields = require_not_blank(self.model.source_fields)

    @property
    def dependencies(self) -> tuple[str, ...]:
        return self._source_fields

    def generate(self, row: Row, row_index: int) -> str:
        values = [float(row[field]) for field in self._source_fields]
        if self.model.value is not None:
            values.append(float(self.model.value))
        return str(prod(values))


class FormulaColumn(ColumnGenerator):
    """Arithmetic over the source fields, which the formula reads as values[0], values[1], ..."""

    def __init__(self, model: ColumnModel) -> None:
        self._source_fields: tuple[str, ...] = ()
        self._expression: ast.expr | None = None
        super().__init__(model)

    def validate(self) -> None:
        self.require("source_fields", "formula")
        self._source_fields = require_not_blank(self.model.source_fields)
        try:
            self._expression = ast.parse(require_not_blank(self.model.formula), mode="eval").body
            check_formula(self._expression, len(self._source_fields))
        except (SyntaxError, ValueError) as error:
            raise ValueError(f"Column {self.model.name} has an invalid formula: {error}") from error

    @property
    def dependencies(self) -> tuple[str, ...]:
        return self._source_fields

    def generate(self, row: Row, row_index: int) -> str:
        values = [float(row[field]) for field in self._source_fields]
        return str(evaluate_formula(self._expression, values))


class DateWithRandomDayOffsetColumn(ColumnGenerator):
    """A date between min and max days after the source field's date."""

    def validate(self) -> None:
        self.require("source_field")
        self._min_days = require_or_default(self.model.min, DEFAULT_MIN_OFFSET_DAYS)
        self._max_days = require_or_default(self.model.max, DEFAULT_MAX_OFFSET_DAYS)
        should_not_be_negative(int(self._min_days), int(self._max_days),
                               error_message=f"Column {self.model.name} needs non-negative day offsets.")
        check_min_max(self._min_days, self._max_days)

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (self.model.source_field,)  # type: ignore[return-value]

    def generate(self, row: Row, row_index: int) -> str:
        base_date = date.fromisoformat(self.get_by_source(row))
        return random_date_from(base_date, self._min_days, self._max_days, self.rand)


class EmailFromSourceFieldsColumn(ColumnGenerator):
    DEFAULT_DOMAIN = "example.com"

    def __init__(self, model: ColumnModel) -> None:
        self._source_fields: tuple[str, ...] = ()
        super().__init__(model)

    def validate(self) -> None:
        self.require("source_fields")
        self._source_fields = require_not_blank(self.model.source_fields)

    @property
    def dependencies(self) -> tuple[str, ...]:
        return self._source_fields

    def generate(self, row: Row, row_index: int) -> str:
        domain = self.model.domain or self.DEFAULT_DOMAIN
        try:
            local_part = ".".join(
                to_email_local_part(
                    require_not_blank(row.get(field), f"Column {self.model.name} depends on source field {field}.")
                )
                for field in self._source_fields
            )
        except ValueError as error:
            raise ValueError(f"Column {self.model.name}: {error}") from error
        return f"{local_part}@{domain}"


class ConcatFromSourceFieldsColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("source_fields")

    @property
    def dependencies(self) -> tuple[str, ...]:
        return require_not_blank(self.model.source_fields)

    def generate(self, row: Row, row_index: int) -> str:
        separator = self.model.separator or " "
        return separator.join(require_not_blank(row.get(field)) for field in self.dependencies)


class NullableColumnGenerator(ColumnGenerator):
    def __init__(self, delegate: ColumnGenerator, probability: float | None):
        self.delegate = delegate
        self.probability = DEFAULT_NULL_PROBABILITY if probability is None else probability
        super().__init__(delegate.model)

    @property
    def seed(self) -> str:
        # Null decisions use their own random stream, independent of the delegate's values.
        return f"{super().seed}:null"

    @property
    def dependencies(self) -> tuple[str, ...]:
        return self.delegate.dependencies

    def generate(self, row: Row, row_index: int) -> str:
        if self.rand.random() < self.probability:
            return ""
        return self.delegate.generate(row, row_index)
