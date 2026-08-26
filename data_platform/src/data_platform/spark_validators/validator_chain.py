from typing import Any

from data_platform.validators.assessment import Assessment


class SparkValidatorChain:
    def __init__(self, validators: tuple[Any, ...] = ()) -> None:
        self.validators = validators

    def validate(self, dataframe: Any) -> Assessment:
        accepted = dataframe
        rejected = dataframe.limit(0)
        errors = []
        for validator in self.validators:
            assessment = validator.validate(accepted)
            accepted = assessment.accepted
            rejected = rejected.unionByName(assessment.rejected, allowMissingColumns=True)
            errors.extend(assessment.errors)
        return Assessment(accepted, rejected, tuple(errors))
