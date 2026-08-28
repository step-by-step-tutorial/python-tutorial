from sklearn.ensemble import RandomForestRegressor


class RegressorBuilder:
    def __init__(
            self,
            model_type: str,
            n_estimators: int,
            n_jobs: int,
            random_state: int,
    ) -> None:
        self._model_type = model_type
        self._n_estimators = n_estimators
        self._n_jobs = n_jobs
        self._random_state = random_state

    def build(self) -> RandomForestRegressor:
        if self._model_type != "random_forest":
            raise ValueError(f"Unsupported model type: {self._model_type}")

        return RandomForestRegressor(
            n_estimators=self._n_estimators,
            random_state=self._random_state,
            n_jobs=self._n_jobs,
        )
