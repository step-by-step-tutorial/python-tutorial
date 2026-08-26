import os
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class ApiSettings:
    url: str


api = MappingProxyType({"data_simulator": ApiSettings(os.getenv("DATA_SIMULATOR_API_URL", "http://localhost:8080"))})
