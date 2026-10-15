from pathlib import Path

from test_data_platform.model.settings_model import SettingsModel
from test_data_platform.repository.dataset_repository import DatasetRepository
from test_data_platform.util.file_utils import list_file_names


def test_dataset_repository_discovers_dataset_names_without_prefix(tmp_path: Path, monkeypatch) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "alpha.json").write_text(
        '{"row_count": 1, "output_name": "alpha", "kafka_topic": "test-events", "kafka_key_column": "id", "destinations": ["csv"], "columns": [{"name": "id", "type": "sequence", "start": 1, "step": 1}]}',
        encoding="utf-8",
    )
    (config_dir / "beta.json").write_text(
        '{"row_count": 1, "output_name": "beta", "kafka_topic": "test-events", "kafka_key_column": "id", "destinations": ["csv"], "columns": [{"name": "id", "type": "sequence", "start": 1, "step": 1}]}',
        encoding="utf-8",
    )
    (config_dir / "nested").mkdir()

    monkeypatch.setenv("CONFIG_DIR", str(config_dir))
    repository = DatasetRepository(SettingsModel.from_env())

    assert list_file_names(config_dir) == ["alpha.json", "beta.json"]
    assert repository.get_all_names() == ["alpha", "beta"]

    monkeypatch.delenv("CONFIG_DIR", raising=False)


def test_dataset_repository_resolves_config_path_from_dataset_name(tmp_path: Path, monkeypatch) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    path = config_dir / "sale.json"
    path.write_text(
        '{"row_count": 1, "output_name": "sale", "kafka_topic": "test-events", "kafka_key_column": "id", "destinations": ["csv"], "columns": [{"name": "id", "type": "sequence", "start": 1, "step": 1}]}',
        encoding="utf-8",
    )

    monkeypatch.setenv("CONFIG_DIR", str(config_dir))
    repository = DatasetRepository(SettingsModel.from_env())

    assert repository.get_one("sale").output_name == "sale"

    monkeypatch.delenv("CONFIG_DIR", raising=False)
