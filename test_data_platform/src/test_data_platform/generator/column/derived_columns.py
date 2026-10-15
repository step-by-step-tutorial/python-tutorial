import ast
from datetime import date, datetime
from math import prod

from test_data_platform.generator.column.column_generator import ColumnGenerator, Row
from test_data_platform.model.column_model import ColumnModel
from test_data_platform.model.settings_model import SettingsModel
from test_data_platform.repository.source_repository import SourceRepository
from test_data_platform.util.date_utils import random_date_from
from test_data_platform.util.formula_utils import check_formula, evaluate_formula, format_number
from test_data_platform.util.text_utils import to_email_local_part
from test_data_platform.util.validation_utils import default_if_blank, require_not_blank, require_not_greater, require_not_negative

DEFAULT_MIN_OFFSET_DAYS = 1
DEFAULT_MAX_OFFSET_DAYS = 7


class ProductColumn(ColumnGenerator):

    def __init__(self, model: ColumnModel, settings: SettingsModel, source_repository: SourceRepository) -> None:
        self._source_fields: tuple[str, ...] = ()
        super().__init__(model, settings, source_repository)

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
        return format_number(prod(values))


class FormulaColumn(ColumnGenerator):
    """Arithmetic over the source fields, which the formula reads as values[0], values[1], ..."""

    def __init__(self, model: ColumnModel, settings: SettingsModel, source_repository: SourceRepository) -> None:
        self._source_fields: tuple[str, ...] = ()
        self._expression: ast.expr | None = None
        super().__init__(model, settings, source_repository)

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
        return format_number(evaluate_formula(self._expression, values))


class DateWithRandomDayOffsetColumn(ColumnGenerator):
    """A date, or a timestamp for a timestamp source, between min and max days after the source field."""

    def validate(self) -> None:
        self.require("source_field")
        self._min_days = default_if_blank(self.model.min, DEFAULT_MIN_OFFSET_DAYS)
        self._max_days = default_if_blank(self.model.max, DEFAULT_MAX_OFFSET_DAYS)
        require_not_negative(int(self._min_days), int(self._max_days),
                               error_message=f"Column {self.model.name} needs non-negative day offsets.")
        require_not_greater(self._min_days, self._max_days)

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (self.model.source_field,)  # type: ignore[return-value]

    def generate(self, row: Row, row_index: int) -> str:
        source = self.get_by_source(row)
        # A timestamp source keeps its time of day.
        base_date = datetime.fromisoformat(source) if "T" in source else date.fromisoformat(source)
        return random_date_from(base_date, self._min_days, self._max_days, self.rand)


class EmailFromSourceFieldsColumn(ColumnGenerator):
    DEFAULT_DOMAIN = "example.com"

    def __init__(self, model: ColumnModel, settings: SettingsModel, source_repository: SourceRepository) -> None:
        self._source_fields: tuple[str, ...] = ()
        super().__init__(model, settings, source_repository)

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
