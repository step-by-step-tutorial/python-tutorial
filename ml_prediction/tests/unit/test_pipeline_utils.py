from types import SimpleNamespace

import numpy as np

from ml_prediction.utils.pipeline_utils import (
    get_feature_importances,
    get_feature_names,
    get_pipeline,
    get_pipeline_step,
)
from ml_prediction.pipeline.pipeline_step import PipelineStep


def test_get_pipeline_unwraps_model_pipeline() -> None:
    pipeline = SimpleNamespace()

    assert get_pipeline(SimpleNamespace(pipeline=pipeline)) is pipeline
    assert get_pipeline(pipeline) is pipeline


def test_get_pipeline_step_returns_named_step_or_pipeline() -> None:
    estimator = SimpleNamespace()
    pipeline = SimpleNamespace(named_steps={PipelineStep.REGRESSOR: estimator})

    assert get_pipeline_step(pipeline, PipelineStep.REGRESSOR) is estimator
    assert get_pipeline_step(SimpleNamespace(), PipelineStep.REGRESSOR).__class__ is SimpleNamespace


def test_get_feature_importances_normalizes_and_rejects_missing_or_empty_values() -> None:
    assert np.array_equal(get_feature_importances(SimpleNamespace(feature_importances_=[0.2, 0.8])), [0.2, 0.8])
    assert get_feature_importances(SimpleNamespace()) is None
    assert get_feature_importances(SimpleNamespace(feature_importances_=[])) is None


def test_get_feature_names_returns_only_matching_preprocessor_names() -> None:
    pipeline = SimpleNamespace(
        named_steps={
            PipelineStep.PREPROCESSOR: SimpleNamespace(
                get_feature_names_out=lambda: ["numeric__area", "categorical__city"]
            )
        }
    )

    assert get_feature_names(pipeline, 2) == ["numeric__area", "categorical__city"]
    assert get_feature_names(pipeline, 1) is None
