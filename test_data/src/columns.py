

import re
import unicodedata
from abc import ABC, abstractmethod
from datetime import date, timedelta
from random import Random
from typing import Mapping

from application_config import DERIVED_TYPE, ColumnConfig
from exceptions import ConfigurationError, SourceDataError
from sources import SourceRepository

Row = Mapping[str, str]

_EMAIL_SEPARATOR = re.compile(r"[^a-z0-9]+")
_REPEATED_DOTS = re.compile(r"\.+")


def normalize_for_email(value: str) -> str:
    ascii_value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    cleaned = _EMAIL_SEPARATOR.sub(".", ascii_value.lower().strip())
    cleaned = _REPEATED_DOTS.sub(".", cleaned).strip(".")
    if not cleaned:
        raise ValueError("Cannot build email from empty normalized value.")
    return cleaned


class ColumnGenerator(ABC):

    def __init__(self, column: ColumnConfig, sources: SourceRepository, rng: Random) -> None:
        self.column = column
        self._sources = sources
        self._rng = rng
        self._validate()

    @property
    def dependencies(self) -> tuple[str, ...]:
        return ()

    @abstractmethod
    def generate(self, row: Row, row_index: int) -> str:
        pass

    def _validate(self) -> None:
        pass

    def _require(self, *keys: str) -> None:
        missing = [key for key in keys if getattr(self.column, key) is None]
        if missing:
            raise ConfigurationError(
                f"Column {self.column.name!r} of type {self.column.type!r} "
                f"requires: {', '.join(missing)}."
            )

    def _source_value(self, row: Row) -> str:
        source_field = self.column.source_field
        assert source_field is not None  # guaranteed by _validate
        try:
            return row[source_field]
        except KeyError as error:
            raise ConfigurationError(
                f"Column {self.column.name!r} depends on source field {source_field!r}."
            ) from error

    def _mapped_value(self, mapping: Mapping[str, str], key: str) -> str:
        try:
            return mapping[key]
        except KeyError as error:
            raise SourceDataError(
                f"Value {key!r} not found in mapping for column {self.column.name!r}."
            ) from error


class SequenceColumn(ColumnGenerator):

    def generate(self, row: Row, row_index: int) -> str:
        start = self.column.start if self.column.start is not None else 1
        step = self.column.step if self.column.step is not None else 1
        return str(start + row_index * step)


class FixedColumn(ColumnGenerator):

    def _validate(self) -> None:
        self._require("value")

    def generate(self, row: Row, row_index: int) -> str:
        return str(self.column.value)


class RandomIntColumn(ColumnGenerator):

    def _validate(self) -> None:
        self._require("min", "max")
        if self.column.min > self.column.max:  # type: ignore[operator]
            raise ConfigurationError(
                f"Column {self.column.name!r}: 'min' must not be greater than 'max'."
            )

    def generate(self, row: Row, row_index: int) -> str:
        return str(self._rng.randint(self.column.min, self.column.max))  # type: ignore[arg-type]


class RandomDateColumn(ColumnGenerator):

    def _validate(self) -> None:
        self._require("date_start", "date_end")
        try:
            self._start = date.fromisoformat(self.column.date_start)  # type: ignore[arg-type]
            self._end = date.fromisoformat(self.column.date_end)  # type: ignore[arg-type]
        except ValueError as error:
            raise ConfigurationError(
                f"Column {self.column.name!r} needs ISO dates (YYYY-MM-DD): {error}"
            ) from error

        if self._start > self._end:
            raise ConfigurationError(
                f"date_start must be earlier than or equal to date_end: {self.column.name}"
            )
        self._span_days = (self._end - self._start).days

    def generate(self, row: Row, row_index: int) -> str:
        offset = self._rng.randint(0, self._span_days)
        return (self._start + timedelta(days=offset)).isoformat()


class RandomFromFileColumn(ColumnGenerator):

    def _validate(self) -> None:
        self._require("file")

    def generate(self, row: Row, row_index: int) -> str:
        return self._rng.choice(self._sources.values(self.column.file))  # type: ignore[arg-type]


class RandomFromMappedFileColumn(ColumnGenerator):

    def _validate(self) -> None:
        self._require("source_field", "mapping_file", "key_column")
        if self.column.file_column and self.column.file_columns:
            raise ConfigurationError(
                f"Use either file_column or file_columns, not both: {self.column.name}"
            )

        self._file_columns = self.column.file_columns or (
            (self.column.file_column,) if self.column.file_column else ()
        )
        if not self._file_columns:
            raise ConfigurationError(
                f"Column {self.column.name!r} of type {self.column.type!r} "
                f"requires: file_column or file_columns."
            )
        self._separator = self.column.separator if self.column.separator is not None else " "

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (self.column.source_field,)  # type: ignore[return-value]

    def generate(self, row: Row, row_index: int) -> str:
        key = self._source_value(row)
        parts: list[str] = []
        for file_column in self._file_columns:
            mapping = self._sources.mapping(
                self.column.mapping_file,  # type: ignore[arg-type]
                self.column.key_column,  # type: ignore[arg-type]
                file_column,
            )
            source_file = self._mapped_value(mapping, key)
            parts.append(self._rng.choice(self._sources.values(source_file)))

        return self._separator.join(parts)


class LookupFromCsvColumn(ColumnGenerator):

    def _validate(self) -> None:
        self._require("source_field", "mapping_file", "key_column", "value_column")

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (self.column.source_field,)  # type: ignore[return-value]

    def generate(self, row: Row, row_index: int) -> str:
        mapping = self._sources.mapping(
            self.column.mapping_file,  # type: ignore[arg-type]
            self.column.key_column,  # type: ignore[arg-type]
            self.column.value_column,  # type: ignore[arg-type]
        )
        return self._mapped_value(mapping, self._source_value(row))


class SubtotalFromQuantityAndUnitPriceColumn(ColumnGenerator):

    @property
    def dependencies(self) -> tuple[str, ...]:
        return ("quantity", "unit_price")

    def generate(self, row: Row, row_index: int) -> str:
        quantity = float(row["quantity"])
        unit_price = float(row["unit_price"])
        return str(quantity * unit_price)


class TaxFromSubtotalColumn(ColumnGenerator):

    def _validate(self) -> None:
        self.rate = float(self.column.value) if self.column.value is not None else 0.0

    @property
    def dependencies(self) -> tuple[str, ...]:
        return ("subtotal",)

    def generate(self, row: Row, row_index: int) -> str:
        subtotal = float(row["subtotal"])
        return str(subtotal * self.rate)


class TotalAmountColumn(ColumnGenerator):

    @property
    def dependencies(self) -> tuple[str, ...]:
        return ("subtotal", "discount_percent", "shipping_cost", "tax_amount")

    def generate(self, row: Row, row_index: int) -> str:
        subtotal = float(row["subtotal"])
        discount_percent = float(row["discount_percent"])
        shipping_cost = float(row["shipping_cost"])
        tax_amount = float(row["tax_amount"])
        discount_amount = subtotal * discount_percent / 100.0
        return str(subtotal - discount_amount + shipping_cost + tax_amount)


class DeliveryDateFromOrderDateColumn(ColumnGenerator):

    def _validate(self) -> None:
        self._require("source_field")
        self._min_days = self.column.start if self.column.start is not None else 1
        self._max_days = self.column.step if self.column.step is not None else 7
        if self._min_days < 0 or self._max_days < 0:
            raise ConfigurationError(f"Column {self.column.name!r} needs non-negative day offsets.")
        if self._min_days > self._max_days:
            raise ConfigurationError(
                f"Column {self.column.name!r}: 'start' must not be greater than 'step'."
            )

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (self.column.source_field,)  # type: ignore[return-value]

    def generate(self, row: Row, row_index: int) -> str:
        base_date = date.fromisoformat(self._source_value(row))
        offset = self._rng.randint(self._min_days, self._max_days)
        return (base_date + timedelta(days=offset)).isoformat()


class EmailFromNameColumn(ColumnGenerator):

    NAME_FIELDS = ("first_name", "last_name")
    DEFAULT_DOMAIN = "example.com"

    @property
    def dependencies(self) -> tuple[str, ...]:
        return self.NAME_FIELDS

    def generate(self, row: Row, row_index: int) -> str:
        first_name = row.get("first_name")
        last_name = row.get("last_name")
        if not first_name or not last_name:
            raise ConfigurationError(
                f"Column {self.column.name!r} depends on first_name and last_name."
            )

        domain = self.column.domain or self.DEFAULT_DOMAIN
        try:
            local_part = f"{normalize_for_email(first_name)}.{normalize_for_email(last_name)}"
        except ValueError as error:
            raise SourceDataError(f"Column {self.column.name!r}: {error}") from error
        return f"{local_part}@{domain}"


COLUMN_TYPES: dict[str, type[ColumnGenerator]] = {
    "sequence": SequenceColumn,
    "fixed": FixedColumn,
    "random_int": RandomIntColumn,
    "random_date": RandomDateColumn,
    "random_from_file": RandomFromFileColumn,
    "random_from_mapped_file": RandomFromMappedFileColumn,
}

DERIVED_METHODS: dict[str, type[ColumnGenerator]] = {
    "email_from_name": EmailFromNameColumn,
    "lookup_from_csv": LookupFromCsvColumn,
    "subtotal_from_quantity_and_unit_price": SubtotalFromQuantityAndUnitPriceColumn,
    "tax_from_subtotal": TaxFromSubtotalColumn,
    "total_amount": TotalAmountColumn,
    "delivery_date_from_order_date": DeliveryDateFromOrderDateColumn,
}


def build_column_generator(
    column: ColumnConfig,
    sources: SourceRepository,
    rng: Random,
) -> ColumnGenerator:
    if column.type == DERIVED_TYPE:
        if column.method is None:
            raise ConfigurationError(f"Derived column {column.name!r} needs a 'method'.")
        generator_type = DERIVED_METHODS.get(column.method)
        if generator_type is None:
            raise ConfigurationError(f"Unsupported derived method: {column.method}")
    else:
        generator_type = COLUMN_TYPES.get(column.type)
        if generator_type is None:
            raise ConfigurationError(f"Unsupported column type: {column.type}")

    return generator_type(column, sources, rng)
