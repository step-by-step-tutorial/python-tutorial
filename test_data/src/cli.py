import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from exceptions import CsvGeneratorError
from application_config import load_config
from file_utils import output_file_path
from generator import generate_dataset

EXIT_OK = 0
EXIT_ERROR = 1


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate CSV test data from text files.")
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
        config = load_config(config_path.name)
        generate_dataset(config_path)
    except CsvGeneratorError as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_ERROR

    print(f"Generated {config.row_count} rows at: {output_file_path(config.output_file)}")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
