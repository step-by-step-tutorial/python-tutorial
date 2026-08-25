from collections.abc import Iterable
from typing import Any

import pandas as pd

from data_platform.model import ValidationError, ValidationResult


def _result(dataframe: Any, valid_mask: Any, rule: str, message: str) -> ValidationResult:
    invalid = dataframe.loc[~valid_mask].reset_index(drop=True)
    return ValidationResult(
        valid=dataframe.loc[valid_mask].reset_index(drop=True),
        invalid=invalid,
        errors=() if invalid.empty else (ValidationError(rule, message),),
    )


class ValidatorChain:
    def __init__(self, validators: tuple[Any, ...]) -> None:
        self.validators = validators

    def validate(self, dataframe: Any) -> ValidationResult:
        invalid_frames = []
        errors = []
        valid = dataframe
        for validator in self.validators:
            result = validator.validate(valid)
            valid = result.valid
            if not result.invalid.empty:
                invalid_frames.append(result.invalid)
                errors.extend(result.errors)
        invalid = pd.concat(invalid_frames, ignore_index=True) if invalid_frames else dataframe.iloc[0:0].copy()
        return ValidationResult(valid=valid, invalid=invalid, errors=tuple(errors))


class RequiredColumnsValidator:
    def __init__(self, columns: Iterable[str]) -> None:
        self.columns = tuple(columns)

    def validate(self, dataframe: Any) -> ValidationResult:
        missing = tuple(column for column in self.columns if column not in dataframe.columns)
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")
        return ValidationResult(dataframe, dataframe.iloc[0:0].copy())


class NotNullValidator:
    def __init__(self, column: str) -> None:
        self.column = column

    def validate(self, dataframe: Any) -> ValidationResult:
        return _result(dataframe, dataframe[self.column].notna(), f"{self.column}_not_null", f"{self.column} must not be null")


class NonNegativeValidator:
    def __init__(self, column: str) -> None:
        self.column = column

    def validate(self, dataframe: Any) -> ValidationResult:
        return _result(dataframe, dataframe[self.column] >= 0, f"{self.column}_non_negative", f"{self.column} must be non-negative")


class PositiveValidator:
    def __init__(self, column: str) -> None:
        self.column = column

    def validate(self, dataframe: Any) -> ValidationResult:
        return _result(dataframe, dataframe[self.column] > 0, f"{self.column}_positive", f"{self.column} must be positive")
