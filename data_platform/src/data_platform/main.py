import logging
import sys

from data_platform.config.main_settings import settings as main_settings
from data_platform.pipeline.configured_pipeline import ConfiguredPipeline
from data_platform.registry.bootstrap import initialize_registries
from data_platform.registry.dataset_registry import dataset_registry

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

initialize_registries()


def run_pipeline(dataset_name: str) -> None:
    ConfiguredPipeline(dataset_registry.get_item(dataset_name.lower())).run()


def main() -> None:
    run_pipeline(sys.argv[1] if len(sys.argv) > 1 else main_settings.app.dataset_name)


if __name__ == "__main__":
    main()

