import importlib
from pathlib import Path

import env_config
from dataset_registry import DatasetRegistry
from file_utils import list_of_file_names


def test_dataset_registry_discovers_dataset_names_without_prefix(tmp_path: Path, monkeypatch) -> None:
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
    (config_dir / "test_output").mkdir()

    monkeypatch.setenv("CONFIG_DIR", str(config_dir))
    importlib.reload(env_config)
    registry = DatasetRegistry()

    assert list_of_file_names(config_dir) == ["alpha.json", "beta.json"]

    monkeypatch.delenv("CONFIG_DIR", raising=False)
    importlib.reload(env_config)


def test_dataset_registry_resolves_config_path_from_dataset_name(tmp_path: Path, monkeypatch) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    path = config_dir / "sale.json"
    path.write_text(
        '{"row_count": 1, "output_name": "sale", "kafka_topic": "test-events", "kafka_key_column": "id", "destinations": ["csv"], "columns": [{"name": "id", "type": "sequence", "start": 1, "step": 1}]}',
        encoding="utf-8",
    )

    monkeypatch.setenv("CONFIG_DIR", str(config_dir))
    importlib.reload(env_config)
    registry = DatasetRegistry()

    assert registry.get_one("sale.json").config.output_name == "sale"

    monkeypatch.delenv("CONFIG_DIR", raising=False)
    importlib.reload(env_config)
