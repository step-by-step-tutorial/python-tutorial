import subprocess
import sys
import os
from pathlib import Path


def test_should_initialize_domain_registries_in_a_clean_process() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from data_platform.main import dataset_registry; "
                "from data_platform.registry.event_converter_registry import event_converter_registry; "
                    "assert dataset_registry.names() == ('sale', 'house', 'online_shopping'); "
                "assert event_converter_registry.names() == ('sale', 'house')"
            ),
        ],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[2] / "src")},
    )

    assert result.returncode == 0, result.stderr


