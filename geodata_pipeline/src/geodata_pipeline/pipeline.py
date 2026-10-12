import csv
import logging
from dataclasses import asdict

import pyarrow.compute as pc
import pyarrow.parquet as pq

from geodata_pipeline.address import is_target_city, matches_state
from geodata_pipeline.config import PipelineConfig, Target
from geodata_pipeline.converter import to_address_record
from geodata_pipeline.model import ADDRESS_COLUMNS
from geodata_pipeline.repository import GeoDataRepository
from geodata_pipeline.resolver import AddressResolver

logger = logging.getLogger(__name__)

BATCH_SIZE = 50_000
PROGRESS_LOG_INTERVAL = 100_000

# Only the Overture address columns the pipeline reads, so the rest of the file is never decoded.
OVERTURE_COLUMNS = [
    "id",
    "geometry",
    "country",
    "postcode",
    "street",
    "number",
    "unit",
    "postal_city",
    "address_levels",
]


class Pipeline:
    def __init__(self, config: PipelineConfig, repository: GeoDataRepository | None = None) -> None:
        self._config = config
        self._repository = repository or GeoDataRepository(
            config.targets, config.geonames_file, config.postal_codes_file
        )
        self._address_resolver = AddressResolver(self._repository)

    def run(self) -> None:
        self._config.output_dir.mkdir(parents=True, exist_ok=True)

        for target in self._config.targets:
            if not target.input_file.is_file():
                logger.warning("Skipping target state=%s: input file does not exist: %s",
                               target.state_code, target.input_file)
                continue

            self.process_target(target)

    def process_target(self, target: Target) -> None:
        logger.info("Processing target state=%s: input=%s, output=%s",
                    target.state_code, target.input_file, target.output_file)

        parquet_file = pq.ParquetFile(target.input_file)
        columns = [column for column in OVERTURE_COLUMNS if column in parquet_file.schema_arrow.names]
        scanned = 0
        written = 0
        missing_coordinates = 0

        with target.output_file.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=ADDRESS_COLUMNS)
            writer.writeheader()

            for batch in parquet_file.iter_batches(batch_size=BATCH_SIZE, columns=columns):
                scanned += batch.num_rows
                # Drop other countries in Arrow before converting rows to Python objects.
                batch = batch.filter(pc.equal(batch.column("country"), target.country_code))

                for row in batch.to_pylist():
                    if not matches_state(row, target.state, target.state_code):
                        continue

                    city = self._address_resolver.find_city(row, target)

                    if not is_target_city(city, target.cities):
                        continue

                    geoname = self._address_resolver.find_geoname(city, target)
                    record = to_address_record(row, target, city, geoname)

                    if record.latitude is None:
                        missing_coordinates += 1

                    writer.writerow(asdict(record))
                    written += 1

                    if written % PROGRESS_LOG_INTERVAL == 0:
                        logger.info("Target state=%s progress scanned=%s written=%s",
                                    target.state_code, scanned, written)

        logger.info("Finished target state=%s scanned=%s written=%s missing_coordinates=%s output=%s",
                    target.state_code, scanned, written, missing_coordinates, target.output_file)
