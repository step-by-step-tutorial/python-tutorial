from __future__ import annotations

import os
from dataclasses import dataclass

from config.datalake import settings as datalake_settings


@dataclass(frozen=True)
class StreamingSettings:
    starting_offsets: str
    checkpoint_path: str


settings = StreamingSettings(
    starting_offsets=os.getenv("APP_STREAMING_STARTING_OFFSETS", "earliest"),
    checkpoint_path=os.getenv(
        "APP_STREAMING_CHECKPOINT_PATH",
        (
            f"{datalake_settings.scheme}://"
            f"{datalake_settings.bucket_name}/checkpoints/{os.getenv('APP_CHANNEL_ID', 'sale-events')}"
        ),
    ),
)
