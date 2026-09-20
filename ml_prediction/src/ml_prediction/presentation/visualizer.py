from dataclasses import replace
from typing import Any

from ml_prediction.audit.data.artifact_dto import ArtifactDto
from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto
from ml_prediction.presentation.cli_view import CliView
from ml_prediction.presentation.view import View
from ml_prediction.presentation.visualization_view import VisualizationView


class VisualizationFacade:
    def __init__(self, dataset_name: str) -> None:
        self._services: tuple[View, ...] = (
            VisualizationView(dataset_name),
            CliView(),
        )

    def visualize(self, dto: TrainingAuditDto) -> TrainingAuditDto:
        artifacts: list[ArtifactDto] = []
        for service in self._services:
            result: Any = service.render(dto)
            if isinstance(result, tuple):
                artifacts.extend(item for item in result if isinstance(item, ArtifactDto))
        return replace(dto, artifacts=dto.artifacts + tuple(artifacts))
