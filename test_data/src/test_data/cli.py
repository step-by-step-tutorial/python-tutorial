import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from test_data.generator.dataset_generator import DatasetGenerator
from test_data.generator.dataset_registry import DatasetRegistry

EXIT_OK = 0
EXIT_ERROR = 1


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate test data from text files.")
    parser.add_argument(
        "--config",
        help="Path to one JSON config file, for example config/online_shopping.json",
    )
    return parser


def get_config_names(config: str | None) -> list[str]:
    if config is not None:
        return [Path(config).name]

    return DatasetRegistry().get_all_names()


def main(argv: Sequence[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        config_names = get_config_names(args.config)
        datasets = [DatasetGenerator(config_name).write() for config_name in config_names]
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_ERROR

    for dataset in datasets:
        print(f"Generated {dataset.config.row_count} rows by {dataset.name}")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
