import os
from dataclasses import dataclass


@dataclass(frozen=True)
class TestDataSettings:
    api_url: str

    def download_url(self, dataset_name: str) -> str:
        return f"{self.api_url.rstrip('/')}/datasets/{dataset_name.lower()}.json/download?format=json"


test_data = TestDataSettings(
    api_url=os.getenv("TEST_DATA_API_URL", "http://localhost:8080"),
)

