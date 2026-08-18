from __future__ import annotations

import json
from urllib.request import Request

import pandas as pd

from config.settings import settings as main_settings
from connector.rest_connection_factory import get_connection


class HouseRestApiIngestor:
    def __init__(
        self,
        url: str = main_settings.rest["house"].url,
        method: str = main_settings.rest["house"].method,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.url = url
        self.method = method
        self.headers = headers or {}

    def ingest(self) -> pd.DataFrame:
        rest_connection = get_connection("house.rest")
        request = Request(self.url, method=self.method, headers=self.headers)
        with rest_connection.open(request) as response:
            payload = response.read().decode("utf-8")

        data = json.loads(payload)
        if isinstance(data, list):
            return pd.json_normalize(data)
        return pd.json_normalize([data])
