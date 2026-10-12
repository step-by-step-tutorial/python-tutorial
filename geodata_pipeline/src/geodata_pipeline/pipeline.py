import logging
from collections import Counter
from collections.abc import Iterator

from geodata_pipeline.address_matcher import AddressMatcher
from geodata_pipeline.geo_data_repository import GeoDataRepository
from geodata_pipeline.model import AddressModel, OvertureAddressModel, PipelineConfigModel, TargetModel
from geodata_pipeline.util.file_utils import write_csv
from geodata_pipeline.util.parquet_utils import read_column_names, read_rows

logger = logging.getLogger(__name__)

BATCH_SIZE = 50_000
PROGRESS_LOG_INTERVAL = 100_000


class Pipeline:
    def __init__(self, config: PipelineConfigModel, repository: GeoDataRepository | None = None) -> None:
        self._config = config
        self._repository = repository or GeoDataRepository.from_files(
            config.targets, config.geonames_file, config.postal_codes_file
        )
        self._address_matcher = AddressMatcher(self._repository)

    def run(self) -> None:
        self._config.output_dir.mkdir(parents=True, exist_ok=True)

        for target in self._config.targets:
            if not target.input_file.is_file():
                logger.warning("Skipping target state=%s: input file does not exist: %s",
                               target.state_code, target.input_file)
                continue

            self.process_target(target)

    def process_target(self, target: TargetModel) -> None:
        logger.info("Processing target state=%s: input=%s, output=%s",
                    target.state_code, target.input_file, target.output_file)
        counts: Counter[str] = Counter()

        write_csv(target.output_file, AddressModel, self._match_addresses(target, counts))

        logger.info("Finished target state=%s scanned=%s written=%s missing_coordinates=%s output=%s",
                    target.state_code, counts["scanned"], counts["written"], counts["missing_coordinates"],
                    target.output_file)

    def _match_addresses(self, target: TargetModel, counts: Counter[str]) -> Iterator[AddressModel]:
        """Yield the output records of the target's addresses, counting scanned and written rows."""
        columns = OvertureAddressModel.columns_in(read_column_names(target.input_file))
        rows = read_rows(target.input_file, columns, BATCH_SIZE, where={"country": target.country_code})

        for row in rows:
            counts["scanned"] += 1
            record = self._address_matcher.match(OvertureAddressModel.from_row(row), target)

            if record is None:
                continue

            counts["written"] += 1

            if record.latitude is None:
                counts["missing_coordinates"] += 1

            if counts["written"] % PROGRESS_LOG_INTERVAL == 0:
                logger.info("Target state=%s progress scanned=%s written=%s",
                            target.state_code, counts["scanned"], counts["written"])

            yield record
