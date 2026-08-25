from typing import Any

import pandas as pd

from data_platform.validators.assessment import Assessment


class ValidatorChain:
    def __init__(self, validators: tuple[Any, ...] = ()) -> None:
        self.validators = validators

    def validate(self, dataframe: Any) -> Assessment:
        accepted = dataframe
        rejected = [pd.DataFrame()]
        errors = []

        for validator in self.validators:
            assessment = validator.validate(accepted)
            accepted = assessment.accepted
            rejected.append(assessment.rejected)
            errors.extend(assessment.errors)

        return Assessment(accepted=accepted, rejected=pd.concat(rejected, ignore_index=True), errors=tuple(errors))
