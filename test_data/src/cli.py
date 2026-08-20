

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from exceptions import CsvGeneratorError
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
        result = generate_dataset(Path(args.config))
    except CsvGeneratorError as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_ERROR

    print(f"Generated {result.row_count} rows at: {result.output_path}")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
