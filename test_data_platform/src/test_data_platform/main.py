import argparse
import logging
import sys
from collections.abc import Sequence

from test_data_platform.generator.dataset_generator import DatasetGenerator
from test_data_platform.model.settings_model import SettingsModel
from test_data_platform.repository.dataset_repository import DatasetRepository

EXIT_OK = 0
EXIT_ERROR = 1


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate test data from text files.")
    parser.add_argument(
        "--config",
        help="Config name in the config directory (online_shopping) or path to a JSON config file. "
             "Without it, every config in the config directory is generated.",
    )
    return parser


def get_config_names(config: str | None, settings: SettingsModel) -> list[str]:
    if config is not None:
        return [config]

    return DatasetRepository(settings).get_all_names()


def main(argv: Sequence[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        settings = SettingsModel.from_env()
        config_names = get_config_names(args.config, settings)
        configs = [DatasetGenerator(config_name, settings).write() for config_name in config_names]
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_ERROR

    for config in configs:
        print(f"Generated {config.row_count} rows by {config.dataset_name}")
    return EXIT_OK


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
    raise SystemExit(main())
