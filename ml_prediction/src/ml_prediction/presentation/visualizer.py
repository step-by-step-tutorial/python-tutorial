from dataclasses import replace
from pathlib import Path
from typing import Any

from ml_prediction.audit.data.artifact_data import ArtifactData
from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.presentation.cli_experiment_presenter import CliExperimentPresenter
from ml_prediction.audit.data.experiment_audit_data import ExperimentAuditData
from ml_prediction.audit.data_service import DataService
from ml_prediction.presentation.presenter import Presenter
from ml_prediction.presentation.visualization_service import VisualizationService


class Visualizer(DataService):
    def __init__(self, dataset_name: str) -> None:
        self._services: tuple[Presenter, ...] = (
            VisualizationService(dataset_name),
            CliExperimentPresenter(),
        )

    def read(self, path: Path) -> tuple[ArtifactData, ...]:
        return ()

    def write(self, data: AuditData, path: Path) -> AuditData | None:
        if not isinstance(data, ExperimentAuditData):
            return None

        artifacts: list[ArtifactData] = []
        for service in self._services:
            result: Any = service.present(data)
            if isinstance(result, tuple):
                artifacts.extend(item for item in result if isinstance(item, ArtifactData))
        return replace(data, artifacts=data.artifacts + tuple(artifacts))
