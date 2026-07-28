from __future__ import annotations

import argparse
from pathlib import Path

from generator_service import CsvDataGenerator, load_config


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate CSV test data from text files.")
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to the JSON config file. Default: config.json",
    )
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    project_root = config_path.parent
    config = load_config(config_path)

    generator = CsvDataGenerator(config=config, project_root=project_root)
    rows = generator.generate_rows()
    output_path = generator.write_csv(rows)

    print(f"Generated {len(rows)} rows at: {output_path}")


if __name__ == "__main__":
    main()
