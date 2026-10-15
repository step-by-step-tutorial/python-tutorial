from abc import ABC, abstractmethod
from collections.abc import Mapping
from random import Random

from test_data_platform.model.column_model import ColumnModel
from test_data_platform.model.settings_model import SettingsModel
from test_data_platform.repository.source_repository import SourceRepository
from test_data_platform.util.validation_utils import require_blank, require_key, require_not_blank

Row = Mapping[str, str]

DEFAULT_NULL_PROBABILITY = 0.2


class ColumnGenerator(ABC):

    def __init__(self, model: ColumnModel, settings: SettingsModel, source_repository: SourceRepository) -> None:
        self.model = model
        self.settings = settings
        self.source_repository = source_repository
        self.rand = Random(self.seed)
        self.validate()

    @property
    def seed(self) -> str:
        # One random stream per column: a shared seed would make columns of the same shape move together.
        return f"{self.settings.random_seed}:{self.model.name}"

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
        return require_key(mapping, key, f"'{key}' not found in mapping for column {self.model.name}.")


class NullableColumnGenerator(ColumnGenerator):
    def __init__(self, delegate: ColumnGenerator, probability: float | None):
        self.delegate = delegate
        self.probability = DEFAULT_NULL_PROBABILITY if probability is None else probability
        super().__init__(delegate.model, delegate.settings, delegate.source_repository)

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


class ConditionalColumnGenerator(ColumnGenerator):
    """Generates a value only when the flag column is True, and leaves the column blank otherwise."""

    def __init__(self, delegate: ColumnGenerator, flag_field: str):
        self.delegate = delegate
        self.flag_field = flag_field
        super().__init__(delegate.model, delegate.settings, delegate.source_repository)

    @property
    def dependencies(self) -> tuple[str, ...]:
        return (*self.delegate.dependencies, self.flag_field)

    def generate(self, row: Row, row_index: int) -> str:
        if row.get(self.flag_field) != "True":
            return ""
        return self.delegate.generate(row, row_index)
