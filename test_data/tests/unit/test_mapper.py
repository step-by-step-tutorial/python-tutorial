from pathlib import Path
from types import SimpleNamespace

import importlib
import env_config
from datasets import Dataset, OutputStatus
from mapper import DatasetMapper


class FakeRegistry:

    def __init__(self, project_root: Path, status: OutputStatus) -> None:
        self.project_root = project_root
        self._status = status
        self.status_calls: list[Dataset] = []

    def status(self, dataset: Dataset) -> OutputStatus:
        self.status_calls.append(dataset)
        return self._status


def test_dataset_mapper_builds_summary_and_output_info(tmp_path: Path, monkeypatch) -> None:
    project_root = tmp_path
    config_dir = project_root / "config"
    output_dir = project_root / "output"
    monkeypatch.setenv("PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("CONFIG_DIR", str(config_dir))
    monkeypatch.setenv("OUTPUT_DIR", str(output_dir))
    importlib.reload(env_config)

    output_path = output_dir / "sale.csv"
    dataset = Dataset(
        name="sale.json",
        config=SimpleNamespace(
            row_count=25,
            headers=("country", "name"),
            destinations=("csv", "json"),
        ),
    )

    status = OutputStatus(
        exists=True,
        path=output_path,
        row_count=25,
    )
    mapper = DatasetMapper(FakeRegistry(project_root, status))

    summary = mapper.summary(dataset)

    assert summary.name == "sale.json"
    assert summary.config_file == "config/sale.json"
    assert summary.configured_row_count == 25
    assert summary.column_count == 2
    assert summary.destinations == ["csv", "json"]
    assert summary.output.exists is True
    assert summary.output.file == "output/sale.csv"
    assert summary.output.row_count == 25

    monkeypatch.delenv("PROJECT_ROOT", raising=False)
    monkeypatch.delenv("CONFIG_DIR", raising=False)
    monkeypatch.delenv("OUTPUT_DIR", raising=False)
    importlib.reload(env_config)
