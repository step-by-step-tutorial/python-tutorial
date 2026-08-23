import subprocess
import sys


def test_should_initialize_domain_registries_in_a_clean_process() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from data_platform.main import dataset_registry; "
                "from data_platform.registry.event_converter_registry import event_converter_registry; "
                "from data_platform.registry.ingestor_registry import ingestor_registry; "
                "assert dataset_registry.names() == ('sale', 'house'); "
                "assert event_converter_registry.names() == ('sale', 'house'); "
                "assert ingestor_registry.contains('house.file.csv')"
            ),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
