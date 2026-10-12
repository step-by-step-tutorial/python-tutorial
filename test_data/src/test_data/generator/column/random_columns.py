from test_data.generator.column.column_generator import ColumnGenerator, Row
from test_data.model.column_model import ColumnModel
from test_data.model.settings_model import SettingsModel
from test_data.repository.source_repository import SourceRepository
from test_data.util.date_utils import days_between, random_date_between
from test_data.util.validation_utils import require_iso_date, require_not_blank, require_not_greater


class RandomIntColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("min", "max")
        require_not_greater(
            minimum=self.model.min,
            maximum=self.model.max,
            error_message=f"Column {self.model.name}: 'min' must not be greater than 'max'."
        )

    def generate(self, row: Row, row_index: int) -> str:
        return str(self.rand.randint(self.model.min, self.model.max))  # type: ignore[arg-type]


class RandomFloatColumn(ColumnGenerator):

    def validate(self) -> None:
        self.require("min", "max")
        require_not_greater(
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
