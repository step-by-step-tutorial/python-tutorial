from __future__ import annotations

from dataclasses import dataclass

from config.datalake import settings as datalake_settings
from config.messaging import settings as messaging_settings


@dataclass(frozen=True)
class StreamingSettings:
    bootstrap_servers: str
    starting_offsets: str
    checkpoint_path: str


settings = StreamingSettings(
    bootstrap_servers=messaging_settings.bootstrap_servers,
    starting_offsets=messaging_settings.starting_offsets,
    checkpoint_path=(
        f"{datalake_settings.scheme}://"
        f"{datalake_settings.bucket_name}/checkpoints/{messaging_settings.topic}"
    ),
)
