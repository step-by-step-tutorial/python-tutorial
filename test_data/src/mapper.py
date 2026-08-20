from __future__ import annotations

from pathlib import Path

import env_config
from datasets import Dataset, DatasetRegistry
from schemas import DatasetSummary, OutputInfo


class DatasetMapper:

    def __init__(self, registry: DatasetRegistry) -> None:
        self._registry = registry

    def relative(self, path: Path) -> str:
        try:
            return path.relative_to(env_config.PROJECT_ROOT).as_posix()
        except ValueError:
            return path.as_posix()

    def output_info(self, dataset: Dataset) -> OutputInfo:
        status = self._registry.status(dataset)
        return OutputInfo(
            exists=status.exists,
            file=self.relative(status.path),
            row_count=status.row_count,
        )

    def summary(self, dataset: Dataset) -> DatasetSummary:
        return DatasetSummary(
            name=dataset.name,
            config_file=self.relative(env_config.CONFIG_DIR / dataset.name),
            configured_row_count=dataset.row_count,
            column_count=len(dataset.columns),
            destinations=list(dataset.destinations),
            output=self.output_info(dataset),
        )
