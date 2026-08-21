import ast
from abc import ABC, abstractmethod
from datetime import date
from math import prod
from random import Random
from typing import Mapping

from data_converter import convert_to_email, random_date_between, random_date_from
from schemas import ColumnModel
from sources_repository import SourceRepository
from validation_utils import (
    check_min_max,
    check_negative_days,
    require_blank,
    require_not_blank,
    require_or_default,
    require_or_raise,
    require_iso_date,
    require_xor, should_not_be_negative, )

Row = Mapping[str, str]


class ColumnGenerator(ABC):

    def __init__(self, column: ColumnModel, sources: SourceRepository, random: Random) -> None:
        self.column = column
        self.sources = sources
        self.random = random
        self.validate()

    @property
    def dependencies(self) -> tuple[str, ...]:
        return ()

    @abstractmethod
    def generate(self, row: Row, row_index: int) -> str:
        pass

    def validate(self) -> None:
        pass

    def require(self, *keys: str) -> None:
        missing = [key for key in keys if getattr(self.column, key) is None]
        require_blank(
            missing,
            error_message=f"Column {self.column.name} of type {self.column.type} requires: {', '.join(missing)}.",
        )

    def get_by_source(self, row: Row) -> str:
        source_field = require_not_blank(self.column.source_field)
        return require_not_blank(row.get(source_field),
                                 f"Column {self.column.name} depends on source field {source_field}.")

    def get_by_key(self, mapping: Mapping[str, str], key: str) -> str:
        return require_or_raise(mapping, key, f"'{key}' not found in mapping for column {self.column.name}.")


class SequenceColumn(ColumnGenerator):

    def generate(self, row: Row, row_index: int) -> str:
        return str(require_or_default(self.column.start, 1) + row_index * require_or_default(self.column.step, 1))


class FixedColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("value")

    def generate(self, row: Row, row_index: int) -> str:
        return str(require_not_blank(self.column.value))


class RandomIntColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("min", "max")
        check_min_max(
            minimum=self.column.min,
            maximum=self.column.max,
            error_message=f"Column {self.column.name}: 'min' must not be greater than 'max'."
        )

    def generate(self, row: Row, row_index: int) -> str:
        return str(self.random.randint(self.column.min, self.column.max))  # type: ignore[arg-type]


class RandomDateColumn(ColumnGenerator):

    def __init__(self, column: ColumnModel, sources: SourceRepository, random: Random):
        self.start = None
        self.end = None
        super().__init__(column, sources, random)

    def validate(self) -> None:
        self.require("date_start", "date_end")
        self.start = require_iso_date(self.column.date_start)
        self.end = require_iso_date(self.column.date_end)
        check_negative_days(
            require_not_blank(self.start),
            require_not_blank(self.end),
            error_message=f"date_start must be earlier than or equal to date_end: {self.column.name}",
        )

    def generate(self, row: Row, row_index: int) -> str:
        return random_date_between(self.start, self.end, self.random)


class RandomFromFileColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("file")

    def generate(self, row: Row, row_index: int) -> str:
        return self.random.choice(self.sources.read_text_file(self.column.file))  # type: ignore[arg-type]


class RandomFromMappedFileColumn(ColumnGenerator):

    def __init__(self, column: ColumnModel, sources: SourceRepository, random: Random):
        self.file_columns = None
        self.separator = None
        super().__init__(column, sources, random)

    def validate(self) -> None:
        self.require("source_field", "mapping_file", "key_column")
        require_xor(
            obj1=self.column.file_column,
            obj2=self.column.file_columns,
            error_message=f"Column {self.column.name} of type {self.column.type} requires: XOR of file_column and file_columns."
        )

        self.file_columns = require_or_default(obj=self.column.file_columns, default=(self.column.file_column,))
        self.separator = require_or_default(obj=self.column.separator, default=" ")

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (require_not_blank(self.column.source_field),)

    def generate(self, row: Row, row_index: int) -> str:
        key = self.get_by_source(row)
        parts: list[str] = []
        for value_column in self.file_columns:
            mapping = self.sources.read_csv_file(
                require_not_blank(self.column.mapping_file),
                require_not_blank(self.column.key_column),
                value_column
            )
            source_file = self.get_by_key(mapping, key)
            parts.append(self.random.choice(self.sources.read_text_file(source_file)))

        return self.separator.join(parts)


class LookupFromCsvColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("source_field", "mapping_file", "key_column", "value_column")

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (require_not_blank(self.column.source_field),)

    def generate(self, row: Row, row_index: int) -> str:
        mapping = self.sources.read_csv_file(
            require_not_blank(self.column.mapping_file),
            require_not_blank(self.column.key_column),
            require_not_blank(self.column.value_column),
        )
        return self.get_by_key(mapping, self.get_by_source(row))


class ProductColumn(ColumnGenerator):

    def __init__(self, column: ColumnModel, sources: SourceRepository, random: Random) -> None:
        self._source_fields: tuple[str, ...] = ()
        super().__init__(column, sources, random)

    def validate(self) -> None:
        self.require("source_fields")
        self._source_fields = require_not_blank(self.column.source_fields)

    @property
    def dependencies(self) -> tuple[str, ...]:
        return self._source_fields

    def generate(self, row: Row, row_index: int) -> str:
        values = [float(row[field]) for field in self._source_fields]
        if self.column.value is not None:
            values.append(float(self.column.value))
        return str(prod(values))


class FormulaColumn(ColumnGenerator):

    def __init__(self, column: ColumnModel, sources: SourceRepository, random: Random) -> None:
        self._source_fields: tuple[str, ...] = ()
        self._formula = ""
        super().__init__(column, sources, random)

    def validate(self) -> None:
        self.require("source_fields", "formula")
        self._source_fields = require_not_blank(self.column.source_fields)
        self._formula = require_not_blank(self.column.formula)
        self._validate_formula()

    @property
    def dependencies(self) -> tuple[str, ...]:
        return self._source_fields

    def generate(self, row: Row, row_index: int) -> str:
        values = [float(row[field]) for field in self._source_fields]
        return str(eval(self._formula, {"__builtins__": {}}, {"values": values}))

    def _validate_formula(self) -> None:
        try:
            ast.parse(self._formula, mode="eval")
        except SyntaxError as error:
            raise Exception(f"Column {self.column.name} has an invalid formula.") from error


class DateWithRandomDayOffsetColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("source_field")
        self._min_days = require_or_default(self.column.start, 1)
        self._max_days = require_or_default(self.column.step, 7)
        should_not_be_negative(int(self._min_days), int(self._max_days),
                               error_message=f"Column {self.column.name} needs non-negative day offsets.")
        check_min_max(self._min_days, self._max_days)

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (self.column.source_field,)  # type: ignore[return-value]

    def generate(self, row: Row, row_index: int) -> str:
        base_date = date.fromisoformat(self.get_by_source(row))
        return random_date_from(base_date, self._min_days, self._max_days, self.random)


class EmailFromSourceFieldsColumn(ColumnGenerator):
    DEFAULT_DOMAIN = "example.com"

    def __init__(self, column: ColumnModel, sources: SourceRepository, random: Random) -> None:
        self._source_fields: tuple[str, ...] = ()
        super().__init__(column, sources, random)

    def validate(self) -> None:
        self.require("source_fields")
        self._source_fields = require_not_blank(self.column.source_fields)

    @property
    def dependencies(self) -> tuple[str, ...]:
        return self._source_fields

    def generate(self, row: Row, row_index: int) -> str:
        domain = self.column.domain or self.DEFAULT_DOMAIN
        try:
            local_part = ".".join(
                convert_to_email(
                    require_not_blank(row.get(field), f"Column {self.column.name} depends on source field {field}.")
                )
                for field in self._source_fields
            )
        except ValueError as error:
            raise Exception(f"Column {self.column.name}: {error}") from error
        return f"{local_part}@{domain}"


generator_registry: dict[str, type[ColumnGenerator]] = {
    "sequence": SequenceColumn,
    "fixed": FixedColumn,
    "random_int": RandomIntColumn,
    "random_date": RandomDateColumn,
    "random_from_file": RandomFromFileColumn,
    "random_from_mapped_file": RandomFromMappedFileColumn,
    "email_from_source_fields": EmailFromSourceFieldsColumn,
    "lookup_from_csv": LookupFromCsvColumn,
    "product_of_source_fields": ProductColumn,
    "formula": FormulaColumn,
    "date_with_random_day_offset": DateWithRandomDayOffsetColumn,
}


def get_column_generator(column: ColumnModel, sources: SourceRepository, random: Random) -> ColumnGenerator:
    generator_name = column.method or column.type
    generator_type = generator_registry.get(generator_name)
    require_not_blank(generator_type, f"Unsupported column generator: {generator_name}")

    return generator_type(column, sources, random)
