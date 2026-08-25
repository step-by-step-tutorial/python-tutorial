from collections.abc import Iterable
from typing import Any

from data_platform.util.dataframe_utils import empty_compatible_dataframe
from data_platform.validators.assessment import Assessment
from data_platform.validators.validator import Validator
from data_platform.validators.data_validator_utils import require_not_blank, require_columns


class RequiredColumnsValidator:
    def __init__(self, columns: Iterable[str]) -> None:
        self.columns = tuple(columns)

    def validate(self, dataframe: Any) -> Assessment:
        require_not_blank(dataframe, "dataframe must not be None")
        require_columns(dataframe, self.columns)
        return Assessment(dataframe, empty_compatible_dataframe(dataframe))


class NotNullValidator(Validator):
    def __init__(self, column: str) -> None:
        self.column = column
        self.rule = f"{column}_not_null"
        self.message = f"{column} must not be null"

    def make_mask(self, dataframe: Any) -> Any:
        return dataframe[self.column].notna()


class NonNegativeValidator(Validator):
    def __init__(self, column: str) -> None:
        self.column = column
        self.rule = f"{column}_non_negative"
        self.message = f"{column} must be non-negative"

    def make_mask(self, dataframe: Any) -> Any:
        return dataframe[self.column] >= 0


class PositiveValidator(Validator):
    def __init__(self, column: str) -> None:
        self.column = column
        self.rule = f"{column}_positive"
        self.message = f"{column} must be positive"

    def make_mask(self, dataframe: Any) -> Any:
        return dataframe[self.column] > 0
