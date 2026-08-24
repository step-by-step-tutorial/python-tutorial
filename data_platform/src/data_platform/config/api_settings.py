import os
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class ApiSettings:
    url: str


api = MappingProxyType({"test_data": ApiSettings(os.getenv("TEST_DATA_API_URL", "http://localhost:8080"))})

