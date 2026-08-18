from __future__ import annotations

import json
from urllib.request import Request, build_opener

import pandas as pd

from dataset.definition import RestApiEndpoint


class RestApiIngestor:
    def __init__(self, endpoint: RestApiEndpoint) -> None:
        self.endpoint = endpoint

    def ingest(self) -> pd.DataFrame:
        rest_connection = build_opener()
        request = Request(self.endpoint.url, method=self.endpoint.method, headers=self.endpoint.headers)
        with rest_connection.open(request) as response:
            payload = response.read().decode("utf-8")

        data = json.loads(payload)
        if isinstance(data, list):
            return pd.json_normalize(data)
        return pd.json_normalize([data])
