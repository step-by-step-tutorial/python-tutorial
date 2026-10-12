from typing import Any

import pandas as pd

from data_platform.model.assessment_model import AssessmentModel


class ValidatorChain:
    def __init__(self, validators: tuple[Any, ...] = ()) -> None:
        self.validators = validators

    def validate(self, dataframe: Any) -> AssessmentModel:
        accepted = dataframe
        rejected = []
        errors = []

        for validator in self.validators:
            assessment = validator.validate(accepted)
            accepted = assessment.accepted
            rejected.append(assessment.rejected)
            errors.extend(assessment.errors)

        return AssessmentModel(accepted=accepted, rejected=self.combine(dataframe, rejected), errors=tuple(errors))

    def combine(self, source: Any, rejected: list[Any]) -> Any:
        return pd.concat([pd.DataFrame(), *rejected], ignore_index=True)
