import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

from geodata_pipeline.model import PipelineConfigModel
from geodata_pipeline.pipeline import Pipeline

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_FILE = Path("config/targets.json")


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="geodata_pipeline", description="Build city address CSV files from Overture Maps and GeoNames data.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_FILE,
        help=f"Path to the pipeline JSON config. Default: {DEFAULT_CONFIG_FILE}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = create_parser().parse_args(argv)

    config = PipelineConfigModel.from_file(args.config)
    missing_files = [path for path in config.source_files if not path.is_file()]

    if missing_files:
        logger.error("GeoNames files not found, see README.md for downloads: %s", [str(path) for path in missing_files])
        return 1

    logger.info("Starting geospatial data pipeline: config=%s", args.config)
    Pipeline(config).run()
    logger.info("Geospatial data pipeline completed")
    return 0
