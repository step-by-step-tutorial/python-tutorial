from typing import Any

from data_platform.validators.assessment import Assessment
from data_platform.validators.data_validator_utils import is_not_blank, require_or_default
from data_platform.validators.violation import Violation


class Validator:
    rule: str
    message: str

    def make_mask(self, dataframe: Any) -> Any:
        raise NotImplementedError

    def validate(self, dataframe: Any) -> Assessment:
        mask = self.make_mask(dataframe)
        accepted_rows = dataframe[mask].reset_index(drop=True)
        rejected_rows = dataframe[~mask].reset_index(drop=True)
        errors = (Violation(self.rule, self.message),) if is_not_blank(rejected_rows) else ()

        return Assessment(
            accepted=require_or_default(accepted_rows, []),
            rejected=require_or_default(rejected_rows, []),
            errors=errors,
        )
