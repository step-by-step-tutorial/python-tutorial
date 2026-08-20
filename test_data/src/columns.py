from abc import ABC, abstractmethod
from datetime import date, timedelta
from random import Random
from typing import Mapping

from config_manager import DERIVED_TYPE, ColumnConfig
from data_converter import convert_to__email, random_date
from sources import SourceRepository
from validation_utils import (
    check_min_max,
    check_negative_days,
    require_blank,
    require_not_blank,
    require_or_default,
    require_or_raise,
    require_iso_date,
    require_xor,
)

Row = Mapping[str, str]


class ColumnGenerator(ABC):

    def __init__(self, column: ColumnConfig, sources: SourceRepository, random: Random) -> None:
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

    def __init__(self, column: ColumnConfig, sources: SourceRepository, random: Random):
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
        return random_date(self.start, self.end, self.random)


class RandomFromFileColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("file")

    def generate(self, row: Row, row_index: int) -> str:
        return self.random.choice(self.sources.values(self.column.file))  # type: ignore[arg-type]


class RandomFromMappedFileColumn(ColumnGenerator):

    def __init__(self, column: ColumnConfig, sources: SourceRepository, random: Random):
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
        for file_column in self.file_columns:
            mapping = self.sources.mapping(
                require_not_blank(self.column.mapping_file),
                require_not_blank(self.column.key_column),
                file_column
            )
            source_file = self.get_by_key(mapping, key)
            parts.append(self.random.choice(self.sources.values(source_file)))

        return self.separator.join(parts)


class LookupFromCsvColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("source_field", "mapping_file", "key_column", "value_column")

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (require_not_blank(self.column.source_field),)

    def generate(self, row: Row, row_index: int) -> str:
        mapping = self.sources.mapping(
            require_not_blank(self.column.mapping_file),
            require_not_blank(self.column.key_column),
            require_not_blank(self.column.value_column),
        )
        return self.get_by_key(mapping, self.get_by_source(row))


class ProductOfSourceFieldsColumn(ColumnGenerator):

    @property
    def dependencies(self) -> tuple[str, ...]:
        return require_not_blank(self.column.source_fields, f"Column {self.column.name} of type {self.column.type} requires source_fields.")

    def validate(self) -> None:
        source_fields = require_not_blank(
            self.column.source_fields,
            f"Column {self.column.name} of type {self.column.type} requires source_fields.",
        )
        if len(source_fields) != 2:
            raise Exception(
                f"Column {self.column.name} of type {self.column.type} requires exactly two source_fields."
            )

    def generate(self, row: Row, row_index: int) -> str:
        left_field, right_field = require_not_blank(
            self.column.source_fields,
            f"Column {self.column.name} of type {self.column.type} requires source_fields.",
        )
        left_value = float(row[left_field])
        right_value = float(row[right_field])
        return str(left_value * right_value)


class TaxFromSubtotalColumn(ColumnGenerator):

    def validate(self) -> None:
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

    def validate(self) -> None:
        self.require("source_field")
        self._min_days = self.column.start if self.column.start is not None else 1
        self._max_days = self.column.step if self.column.step is not None else 7
        if self._min_days < 0 or self._max_days < 0:
            raise Exception(f"Column {self.column.name} needs non-negative day offsets.")
        if self._min_days > self._max_days:
            raise Exception(
                f"Column {self.column.name}: 'start' must not be greater than 'step'."
            )

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (self.column.source_field,)  # type: ignore[return-value]

    def generate(self, row: Row, row_index: int) -> str:
        base_date = date.fromisoformat(self.get_by_source(row))
        offset = self.random.randint(self._min_days, self._max_days)
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
            raise Exception(
                f"Column {self.column.name} depends on first_name and last_name."
            )

        domain = self.column.domain or self.DEFAULT_DOMAIN
        try:
            local_part = f"{convert_to__email(first_name)}.{convert_to__email(last_name)}"
        except ValueError as error:
            raise Exception(f"Column {self.column.name}: {error}") from error
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
    "product_of_source_fields": ProductOfSourceFieldsColumn,
    "subtotal_from_quantity_and_unit_price": ProductOfSourceFieldsColumn,
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
            raise Exception(f"Derived column {column.name} needs a 'method'.")
        generator_type = DERIVED_METHODS.get(column.method)
        if generator_type is None:
            raise Exception(f"Unsupported derived method: {column.method}")
    else:
        generator_type = COLUMN_TYPES.get(column.type)
        if generator_type is None:
            raise Exception(f"Unsupported column type: {column.type}")

    return generator_type(column, sources, rng)
