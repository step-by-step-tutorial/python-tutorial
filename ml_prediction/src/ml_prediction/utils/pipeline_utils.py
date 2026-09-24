from typing import Any

import numpy as np

from ml_prediction.pipeline.pipeline_step import PipelineStep

def get_pipeline(fitted_model: Any) -> Any:
    return getattr(fitted_model, "pipeline", fitted_model)


def get_pipeline_step(pipeline: Any, step: PipelineStep) -> Any:
    if hasattr(pipeline, "named_steps") and step in pipeline.named_steps:
        return pipeline.named_steps[step]
    return pipeline


def get_feature_importances(estimator: Any) -> np.ndarray | None:
    importances = getattr(estimator, "feature_importances_", None)
    if importances is None:
        return None

    importances = np.asarray(importances)
    return importances if importances.size else None


def get_feature_names(pipeline: Any, count: int) -> list[str] | None:
    if not hasattr(pipeline, "named_steps"):
        return None

    preprocessor = pipeline.named_steps.get(PipelineStep.PREPROCESSOR)
    if preprocessor is None or not hasattr(preprocessor, "get_feature_names_out"):
        return None

    names = list(preprocessor.get_feature_names_out())
    return names if len(names) == count else None
