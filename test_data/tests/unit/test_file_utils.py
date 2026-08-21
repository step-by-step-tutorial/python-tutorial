import importlib
from pathlib import Path

import env_config

from file_utils import absolute_project_path


def test_absolute_project_path_uses_project_root(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))
    importlib.reload(env_config)

    assert absolute_project_path("data/countries.txt") == tmp_path / "data" / "countries.txt"

    monkeypatch.delenv("PROJECT_ROOT", raising=False)
    importlib.reload(env_config)
