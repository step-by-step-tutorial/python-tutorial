import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class SettingsModel:
    """Runtime settings, read from environment variables once at startup and passed to the classes that need them."""
    project_root: Path
    config_dir: Path
    output_dir: Path
    database_url: str
    database_schema: str | None
    kafka_bootstrap_servers: str
    kafka_flush_timeout_seconds: float
    random_seed: int = 42

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "SettingsModel":
        env = os.environ if environ is None else environ
        project_root = Path(env.get("PROJECT_ROOT", DEFAULT_PROJECT_ROOT)).resolve()

        return cls(
            project_root=project_root,
            config_dir=Path(env.get("CONFIG_DIR", project_root / "config")).resolve(),
            output_dir=Path(env.get("OUTPUT_DIR", project_root / "output")).resolve(),
            database_url=env.get("DATABASE_URL", "postgresql+psycopg2://admin:admin@localhost:5432/app_database"),
            # An empty DATABASE_SCHEMA means the database's default schema.
            database_schema=env.get("DATABASE_SCHEMA", "test_data") or None,
            kafka_bootstrap_servers=env.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            kafka_flush_timeout_seconds=float(env.get("KAFKA_FLUSH_TIMEOUT_SECONDS", "5")),
        )

    def project_path(self, relative_path: str | Path) -> Path:
        """Resolve a path from a config (such as data/countries.txt) against the project root."""
        return (self.project_root / relative_path).resolve()
