from dataclasses import replace
from typing import Any

from ml_prediction.audit.data.artifact_data import ArtifactData
from ml_prediction.audit.data.training_audit_data import TrainingAuditData
from ml_prediction.presentation.cli_view import CliView
from ml_prediction.presentation.view import View
from ml_prediction.presentation.visualization_view import VisualizationView


class VisualizationFacade:
    def __init__(self, dataset_name: str) -> None:
        self._services: tuple[View, ...] = (
            VisualizationView(dataset_name),
            CliView(),
        )

    def visualize(self, data: TrainingAuditData) -> TrainingAuditData:
        artifacts: list[ArtifactData] = []
        for service in self._services:
            result: Any = service.render(data)
            if isinstance(result, tuple):
                artifacts.extend(item for item in result if isinstance(item, ArtifactData))
        return replace(data, artifacts=data.artifacts + tuple(artifacts))
