from test_data_platform.generator.column.column_generator import ColumnGenerator, Row
from test_data_platform.model.column_model import ColumnModel
from test_data_platform.model.settings_model import SettingsModel
from test_data_platform.repository.source_repository import SourceRepository
from test_data_platform.util.date_utils import days_between, random_date_between
from test_data_platform.util.validation_utils import require_blank, require_iso_date, require_not_blank, require_not_greater


class RandomRangeColumn(ColumnGenerator):
    """A random number between min and max; min_field or max_field take that bound from another column."""

    def validate(self) -> None:
        missing = [name for name, value, field in (("min", self.model.min, self.model.min_field),
                                                   ("max", self.model.max, self.model.max_field))
                   if value is None and field is None]
        require_blank(missing, error_message=(
            f"Column {self.model.name} of type {self.model.type} requires: {', '.join(missing)} or its _field."
        ))
        if self.model.min is not None and self.model.max is not None:
            require_not_greater(
                minimum=self.model.min,
                maximum=self.model.max,
                error_message=f"Column {self.model.name}: 'min' must not be greater than 'max'.",
            )

    @property
    def dependencies(self) -> tuple[str, ...]:
        return tuple(field for field in (self.model.min_field, self.model.max_field) if field)

    def bounds(self, row: Row) -> tuple[float, float]:
        minimum = self._bound(row, self.model.min_field, self.model.min)
        maximum = self._bound(row, self.model.max_field, self.model.max)
        require_not_greater(minimum, maximum,
                            error_message=f"Column {self.model.name}: 'min' must not be greater than 'max'.")
        return minimum, maximum

    def _bound(self, row: Row, field: str | None, value: int | None) -> float:
        if field is None:
            return value  # type: ignore[return-value]
        return float(require_not_blank(row.get(field), f"Column {self.model.name} depends on source field {field}."))


class RandomIntColumn(RandomRangeColumn):

    def generate(self, row: Row, row_index: int) -> str:
        minimum, maximum = self.bounds(row)
        return str(self.rand.randint(int(minimum), int(maximum)))


class RandomFloatColumn(RandomRangeColumn):

    def generate(self, row: Row, row_index: int) -> str:
        minimum, maximum = self.bounds(row)
        return f"{self.rand.uniform(minimum, maximum):.6f}"


class RandomBooleanColumn(ColumnGenerator):

    def generate(self, row: Row, row_index: int) -> str:
        return str(self.rand.choice((True, False)))


class RandomTimestampColumn(ColumnGenerator):

    def __init__(self, model: ColumnModel, settings: SettingsModel, source_repository: SourceRepository) -> None:
        self.start = None
        self.end = None
        super().__init__(model, settings, source_repository)

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

    def __init__(self, model: ColumnModel, settings: SettingsModel, source_repository: SourceRepository) -> None:
        self.start = None
        self.end = None
        super().__init__(model, settings, source_repository)

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
