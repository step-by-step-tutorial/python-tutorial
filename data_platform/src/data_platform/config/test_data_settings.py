import os
from dataclasses import dataclass

from data_platform.config.app_settings import app

@dataclass(frozen=True)
class TestDataSettings:
    __test__ = False

    api_url: str
    dataset_name: str

    @property
    def download_url(self) -> str:
        return f"{self.api_url.rstrip('/')}/datasets/{self.dataset_name.lower()}.json/download?format=json"

test_data = TestDataSettings(
    api_url=os.getenv("TEST_DATA_API_URL", "http://localhost:8080"),
    dataset_name=app.dataset_name,
)
