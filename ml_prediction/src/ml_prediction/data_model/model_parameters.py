from dataclasses import dataclass


@dataclass(frozen=True)
class ModelParameters:
    n_estimators: int
    n_jobs: int
    max_depth: int | None
    min_samples_split: int
    min_samples_leaf: int
    max_features: int | float | str | None
    bootstrap: bool
    random_state: int

    def as_dict(self) -> dict[str, object]:
        return {
            "n_estimators": self.n_estimators,
            "n_jobs": self.n_jobs,
            "max_depth": self.max_depth,
            "min_samples_split": self.min_samples_split,
            "min_samples_leaf": self.min_samples_leaf,
            "max_features": self.max_features,
            "bootstrap": self.bootstrap,
            "random_state": self.random_state,
        }
