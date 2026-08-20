import importlib
from pathlib import Path

import env_config


def test_project_root_defaults_to_repository_root(monkeypatch) -> None:
    monkeypatch.delenv("CSV_GENERATOR_ROOT", raising=False)

    module = importlib.reload(env_config)

    assert module.PROJECT_ROOT == Path(__file__).resolve().parents[2]


def test_project_root_uses_env_override(monkeypatch, tmp_path) -> None:
    override = tmp_path / "custom-root"
    monkeypatch.setenv("PROJECT_ROOT", str(override))

    module = importlib.reload(env_config)

    assert module.PROJECT_ROOT == override.resolve()
    monkeypatch.delenv("PROJECT_ROOT", raising=False)
    importlib.reload(env_config)


def test_config_dir_defaults_to_project_root_config(monkeypatch) -> None:
    monkeypatch.delenv("CONFIG_DIR", raising=False)

    module = importlib.reload(env_config)

    assert module.CONFIG_DIR == module.PROJECT_ROOT / "config"


def test_config_dir_uses_env_override(monkeypatch, tmp_path) -> None:
    override = tmp_path / "datasets"
    monkeypatch.setenv("CONFIG_DIR", str(override))

    module = importlib.reload(env_config)

    assert module.CONFIG_DIR == override.resolve()
    monkeypatch.delenv("CONFIG_DIR", raising=False)
    importlib.reload(env_config)


def test_output_dir_defaults_to_project_root_output(monkeypatch) -> None:
    monkeypatch.delenv("OUTPUT_DIR", raising=False)

    module = importlib.reload(env_config)

    assert module.OUTPUT_DIR == module.PROJECT_ROOT / "output"


def test_output_dir_uses_env_override(monkeypatch, tmp_path) -> None:
    override = tmp_path / "generated"
    monkeypatch.setenv("OUTPUT_DIR", str(override))

    module = importlib.reload(env_config)

    assert module.OUTPUT_DIR == override.resolve()
    monkeypatch.delenv("OUTPUT_DIR", raising=False)
    importlib.reload(env_config)
