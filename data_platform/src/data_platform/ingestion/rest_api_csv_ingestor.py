import logging
from io import StringIO
from urllib.request import Request, build_opener

import pandas as pd

from data_platform.model.dataset_ingestor import DatasetIngestor
from data_platform.model.endpoints import RestApiEndpoint

logger = logging.getLogger(__name__)


class RestApiCsvIngestor(DatasetIngestor):
    def __init__(self, endpoint: RestApiEndpoint) -> None:
        self._endpoint = endpoint
        self.name = "api"

    def ingest(self) -> pd.DataFrame:
        logger.info("Downloading CSV data from %s", self._endpoint.url)
        request = Request(self._endpoint.url, method=self._endpoint.method, headers=self._endpoint.headers)
        with build_opener().open(request) as response:
            payload = response.read()
            data = pd.read_csv(StringIO(payload.decode("utf-8")))
        logger.info("Downloaded CSV data: url=%s rows=%s columns=%s bytes=%s", self._endpoint.url, len(data),
                    len(data.columns), len(payload))
        return data
