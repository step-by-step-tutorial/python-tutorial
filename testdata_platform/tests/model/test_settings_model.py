from pathlib import Path

from testdata_platform.model.settings_model import SettingsModel

PROJECT_DIR = Path(__file__).resolve().parents[2]


def test_defaults_point_to_the_project_directory() -> None:
    settings = SettingsModel.from_env({})

    assert settings.project_root == PROJECT_DIR
    assert settings.config_dir == PROJECT_DIR / "config"
    assert settings.output_dir == PROJECT_DIR / "output"
    assert settings.database_url == "postgresql+psycopg2://admin:admin@localhost:5432/app_database"
    assert settings.database_schema == "test_data"
    assert settings.kafka_bootstrap_servers == "localhost:9092"
    assert settings.kafka_flush_timeout_seconds == 5.0


def test_directories_follow_project_root_override(tmp_path: Path) -> None:
    settings = SettingsModel.from_env({"PROJECT_ROOT": str(tmp_path)})

    assert settings.project_root == tmp_path
    assert settings.config_dir == tmp_path / "config"
    assert settings.output_dir == tmp_path / "output"


def test_env_overrides(tmp_path: Path) -> None:
    settings = SettingsModel.from_env({
        "CONFIG_DIR": str(tmp_path / "configs"),
        "OUTPUT_DIR": str(tmp_path / "out"),
        "DATABASE_URL": "sqlite://",
        "DATABASE_SCHEMA": "",
        "KAFKA_BOOTSTRAP_SERVERS": "kafka:29092",
        "KAFKA_FLUSH_TIMEOUT_SECONDS": "1.5",
    })

    assert settings.config_dir == tmp_path / "configs"
    assert settings.output_dir == tmp_path / "out"
    assert settings.database_url == "sqlite://"
    assert settings.database_schema is None
    assert settings.kafka_bootstrap_servers == "kafka:29092"
    assert settings.kafka_flush_timeout_seconds == 1.5


def test_from_env_reads_the_process_environment(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path))

    assert SettingsModel.from_env().output_dir == tmp_path


def test_project_path_resolves_against_project_root(tmp_path: Path) -> None:
    settings = SettingsModel.from_env({"PROJECT_ROOT": str(tmp_path)})

    assert settings.project_path("data/countries.txt") == tmp_path / "data" / "countries.txt"
