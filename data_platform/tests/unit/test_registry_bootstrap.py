import os
import subprocess
import sys
from pathlib import Path


def test_should_initialize_domain_registries_in_a_clean_process() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from data_platform.registry.bootstrap import initialize_registries; "
                "from data_platform.registry.dataset_registry import dataset_registry; "
                "initialize_registries(); "
                "assert dataset_registry.names() == ('house', 'online_shopping'), dataset_registry.names()"
            ),
        ],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[2] / "src")},
    )

    assert result.returncode == 0, result.stderr


def test_initialize_registries_is_repeatable() -> None:
    from data_platform.registry.bootstrap import initialize_registries
    from data_platform.registry.dataset_registry import dataset_registry

    initialize_registries()
    initialize_registries()

    assert dataset_registry.names() == ("house", "online_shopping")
