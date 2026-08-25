import json
import logging
from urllib.request import Request, build_opener

import pandas as pd

from data_platform.model.endpoints import RestApiEndpoint

logger = logging.getLogger(__name__)


class RestApiIngestor:
    def __init__(self, endpoint: RestApiEndpoint) -> None:
        self._endpoint = endpoint

    def ingest(self) -> pd.DataFrame:
        logger.info("Ingesting REST API data from %s", self._endpoint.url)
        rest_connection = build_opener()
        request = Request(self._endpoint.url, method=self._endpoint.method, headers=self._endpoint.headers)
        with rest_connection.open(request) as response:
            payload = response.read().decode("utf-8")

        data = json.loads(payload)
        if isinstance(data, list):
            return pd.json_normalize(data)
        return pd.json_normalize([data])

