from pathlib import Path

from ml_prediction.utils.data_validator_utils import require_not_blank

import numpy as np

from ml_prediction.audit.data.artifact_category import ArtifactCategory
from ml_prediction.audit.data.artifact_dto import ArtifactDto
from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto
from ml_prediction.config.settings import get_settings
from ml_prediction.pipeline.pipeline_step import PipelineStep
from ml_prediction.visualize.visualizer import Visualizer
from ml_prediction.utils.pipeline_utils import (
    get_feature_importances,
    get_feature_names,
    get_pipeline,
    get_pipeline_step,
)
from ml_prediction.utils.visualization_utils import save_bar_chart


class ModelInterpretabilityVisualizer(Visualizer):

    def __init__(self, dataset_name: str) -> None:
        self._settings = get_settings(dataset_name)

    def render(self, dto: TrainingAuditDto) -> tuple[ArtifactDto, ...]:
        if dto.model is None:
            return ()

        feature_importance_path = require_not_blank(self.save_feature_importance(dto.model, dto.experiment.run_id))
        return tuple([
            ArtifactDto(feature_importance_path, ArtifactCategory.PLOTS),
        ])

    def save_feature_importance(self, fitted_model, run_id: str, top_n: int = 20) -> Path | None:
        pipeline = get_pipeline(fitted_model)
        regressor = get_pipeline_step(pipeline, PipelineStep.REGRESSOR)
        importances = get_feature_importances(regressor)
        if importances is None:
            return None

        feature_names = get_feature_names(pipeline, len(importances))
        if feature_names is None:
            return None

        order = np.argsort(importances)[::-1][:top_n]
        return save_bar_chart(
            labels=np.asarray(feature_names)[order],
            values=importances[order],
            path=self._settings.artifact_path(run_id, self._settings.feature_importance_filename),
            x_label="Importance",
            y_label="Feature",
            title="Feature importance",
            horizontal=True,
        )
