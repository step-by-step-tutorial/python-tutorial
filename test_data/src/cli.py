import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from generator import DataGenerator

EXIT_OK = 0
EXIT_ERROR = 1


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate test data from text files.")
    parser.add_argument(
        "--config",
        required=True,
        help="Path to the JSON config file, for example config/sale.json",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    try:
        config_path = Path(args.config)
        dataset = DataGenerator(config_path.name).generate_dataset()
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_ERROR

    print(f"Generated {dataset.config.row_count} rows by {config_path}")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
