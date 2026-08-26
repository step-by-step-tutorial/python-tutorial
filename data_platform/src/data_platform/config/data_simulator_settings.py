import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DataSimulatorSettings:
    api_url: str


data_simulator = DataSimulatorSettings(
    api_url=os.getenv("DATA_SIMULATOR_API_URL", "http://localhost:8080"),
)
