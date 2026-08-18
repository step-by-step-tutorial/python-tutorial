from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RestSettings:
    url: str
    method: str


sale_settings = RestSettings(
    url=os.getenv("APP_SALE_REST_URL", "http://localhost:8080"),
    method=os.getenv("APP_SALE_REST_METHOD", "GET"),
)
house_settings = RestSettings(
    url=os.getenv("APP_HOUSE_REST_URL", "http://localhost:8080"),
    method=os.getenv("APP_HOUSE_REST_METHOD", "GET"),
)

settings = sale_settings
