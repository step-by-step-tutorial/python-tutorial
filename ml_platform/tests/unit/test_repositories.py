from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest

from conftest import make_dataframe, make_settings
from ml_platform.config.dataset_profiles import HOUSE
from ml_platform.config.dataset_source import DatasetSource
from ml_platform.config.model_type import ModelType
from ml_platform.config.task_type import TaskType
from ml_platform.model.experiment_model import ExperimentModel
from ml_platform.model.metrics_model import RegressionMetricsModel
from ml_platform.repository import dataset_repository
from ml_platform.repository.datalake_repository import DataLakeRepository
from ml_platform.repository.dataset_repository import DatasetRepository
from ml_platform.repository.experiment_repository import ExperimentRepository


class FakeS3Client:
    def __init__(self, objects: dict[str, tuple[datetime, pd.DataFrame]]) -> None:
        self._objects = objects

    def get_paginator(self, operation: str) -> "FakeS3Client":
        assert operation == "list_objects_v2"
        return self

    def paginate(self, Bucket: str, Prefix: str) -> list[dict]:
        contents = [
            {"Key": key, "LastModified": modified}
            for key, (modified, _) in self._objects.items()
            if key.startswith(Prefix)
        ]
        return [{"Contents": contents}, {}]

    def download_fileobj(self, bucket: str, key: str, buffer: BytesIO) -> None:
        self._objects[key][1].to_parquet(buffer, index=False)


def make_experiment(path: Path) -> ExperimentModel:
    metrics = RegressionMetricsModel(mean_absolute_error=1.0, root_mean_squared_error=2.0, r2_score=0.5)
    return ExperimentModel(
        run_id="run",
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        dataset_name="house",
        task_type=TaskType.REGRESSION,
        model_type=ModelType.RANDOM_FOREST,
        model_parameters={"max_depth": None},
        validation_metrics=metrics,
        test_metrics=metrics,
        model_path=path,
    )


def test_experiment_repository_round_trip(tmp_path: Path) -> None:
    repository = ExperimentRepository(tmp_path / "experiments.csv")
    experiment = make_experiment(tmp_path / "model.joblib")

    repository.append(experiment)
    repository.append(experiment)

    assert repository.find_all() == [experiment, experiment]


def test_experiment_repository_returns_nothing_without_file(tmp_path: Path) -> None:
    assert ExperimentRepository(tmp_path / "missing.csv").find_all() == []


def test_data_lake_repository_downloads_latest_partition(house_settings, tmp_path: Path) -> None:
    old = pd.DataFrame({"value": [1]})
    new = pd.DataFrame({"value": [2, 3]})
    prefix = house_settings.data_lake.object_prefix
    client = FakeS3Client({
        f"{prefix}2026-01-01/part-0.parquet": (datetime(2026, 1, 1), old),
        f"{prefix}2026-01-02/part-0.parquet": (datetime(2026, 1, 2), new),
        f"{prefix}2026-01-02/part-1.parquet": (datetime(2026, 1, 2), new),
        f"{prefix}2026-01-02/_SUCCESS": (datetime(2026, 1, 3), old),
    })

    path = DataLakeRepository(house_settings.data_lake, client).download_latest_partition(tmp_path / "out.csv")

    assert pd.read_csv(path)["value"].tolist() == [2, 3, 2, 3]


def test_data_lake_repository_requires_parquet_files(house_settings, tmp_path: Path) -> None:
    repository = DataLakeRepository(house_settings.data_lake, FakeS3Client({}))

    with pytest.raises(ValueError, match="No Parquet files found"):
        repository.download_latest_partition(tmp_path / "out.csv")


def test_dataset_repository_loads_local_dataset(house_settings) -> None:
    dataframe, path = DatasetRepository(house_settings).load()

    assert path == house_settings.dataset_path
    assert len(dataframe) == 60


def test_dataset_repository_downloads_before_loading(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = make_settings(tmp_path, HOUSE, dataset_source=DatasetSource.DOWNLOAD)

    class FakeDataLakeRepository:
        def __init__(self, data_lake_settings) -> None:
            assert data_lake_settings == settings.data_lake

        def download_latest_partition(self, path: Path) -> Path:
            path.parent.mkdir(parents=True, exist_ok=True)
            make_dataframe(HOUSE, rows=5).to_csv(path, index=False)
            return path

    monkeypatch.setattr(dataset_repository, "DataLakeRepository", FakeDataLakeRepository)

    dataframe, _ = DatasetRepository(settings).load()

    assert len(dataframe) == 5
