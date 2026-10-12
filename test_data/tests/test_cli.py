import json
from pathlib import Path

from test_data import cli
from test_data.model.settings_model import SettingsModel


def test_main_generates_config_by_name(project_root: Path) -> None:
    assert cli.main(["--config", "demo"]) == cli.EXIT_OK
    assert (SettingsModel.from_env().output_dir / "demo.csv").is_file()


def test_main_generates_config_from_path(project_root: Path) -> None:
    config_path = SettingsModel.from_env().config_dir / "demo.json"

    assert cli.main(["--config", str(config_path)]) == cli.EXIT_OK


def test_main_fails_when_a_destination_fails(project_root: Path, capsys) -> None:
    config_path = SettingsModel.from_env().config_dir / "demo.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["destinations"] = ["csv", "unknown"]
    config_path.write_text(json.dumps(config), encoding="utf-8")

    assert cli.main(["--config", "demo"]) == cli.EXIT_ERROR
    assert "unknown" in capsys.readouterr().err
