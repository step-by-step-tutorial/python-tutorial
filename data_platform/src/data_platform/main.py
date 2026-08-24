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


def select_dataset() -> str | None:
    """Display registered datasets and return the selected dataset name."""
    names = dataset_registry.names()
    if not names:
        raise RuntimeError("No datasets are registered.")

    print("Available datasets:")
    for index, name in enumerate(names, start=1):
        print(f"  {index}. {name}")
    print("  0. Exit")

    while True:
        selection = input("Select a dataset: ").strip().lower()
        if selection in {"0", "q", "quit", "exit"}:
            return None
        if selection.isdigit() and 1 <= int(selection) <= len(names):
            return names[int(selection) - 1]
        print(f"Select a number between 1 and {len(names)}, or 0 to exit.")


def main() -> None:
    if len(sys.argv) > 1:
        run_pipeline(sys.argv[1])
        return

    if sys.stdin.isatty():
        dataset_name = select_dataset()
        if dataset_name is not None:
            run_pipeline(dataset_name)
        return

    # Preserve the configured default for containers and scheduled execution.
    run_pipeline(main_settings.app.dataset_name)


if __name__ == "__main__":
    main()

