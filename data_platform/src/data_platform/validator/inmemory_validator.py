from collections.abc import Iterable
from typing import Any

import pandas as pd

from data_platform.model.assessment_model import AssessmentModel
from data_platform.model.violation_model import ViolationModel
from data_platform.util.validation_utils import is_not_blank, require_columns, require_not_blank


class RequiredColumnsValidator:
    def __init__(self, columns: Iterable[str]) -> None:
        self.columns = tuple(columns)

    def validate(self, dataframe: Any) -> AssessmentModel:
        require_not_blank(dataframe, "dataframe must not be None")
        require_columns(dataframe, self.columns)
        return AssessmentModel(dataframe, pd.DataFrame())


class ColumnValidator:
    rule: str
    message: str

    def make_mask(self, dataframe: Any) -> Any:
        raise NotImplementedError

    def validate(self, dataframe: Any) -> AssessmentModel:
        mask = self.make_mask(dataframe)
        accepted_rows = dataframe[mask].reset_index(drop=True)
        rejected_rows = dataframe[~mask].reset_index(drop=True)
        errors = (ViolationModel(self.rule, self.message),) if is_not_blank(rejected_rows) else ()
        return AssessmentModel(accepted=accepted_rows, rejected=rejected_rows, errors=errors)


class NotNullValidator(ColumnValidator):
    def __init__(self, column: str) -> None:
        self.column = column
        self.rule = f"{column}_not_null"
        self.message = f"{column} must not be null"

    def make_mask(self, dataframe: Any) -> Any:
        return dataframe[self.column].notna()


class NonNegativeValidator(ColumnValidator):
    def __init__(self, column: str) -> None:
        self.column = column
        self.rule = f"{column}_non_negative"
        self.message = f"{column} must be non-negative"

    def make_mask(self, dataframe: Any) -> Any:
        return dataframe[self.column] >= 0


class PositiveValidator(ColumnValidator):
    def __init__(self, column: str) -> None:
        self.column = column
        self.rule = f"{column}_positive"
        self.message = f"{column} must be positive"

    def make_mask(self, dataframe: Any) -> Any:
        return dataframe[self.column] > 0
