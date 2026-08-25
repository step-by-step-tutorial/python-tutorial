from data_platform.config.data_lake_environment import StorageEnvironment
from data_platform.model import Dataset, StorageObject
from data_platform.pipeline.pipeline import Pipeline
from data_platform.util.path_utils import extract_filename, generate_relative_path


class DataPipeline(Pipeline):

    def __init__(self, dataset: Dataset) -> None:
        super().__init__(dataset)
        self.flow = dataset.flow

    def prepare(self) -> None:
        self.flow.before_pipeline(self)

    def ingest(self) -> tuple[StorageObject, ...]:
        storage = self.flow.storages[0]
        storage_objects = []
        for ingestor in self.flow.ingestors:
            data = ingestor.ingest()
            path = storage.save(data, f"{self.storage_relative_path}/{ingestor.name}")
            storage_objects.append(StorageObject("storage", path))
        return tuple(storage_objects)

    def clean(self, paths: tuple[StorageObject, ...]) -> tuple[StorageObject, ...]:
        storage = self.flow.storages[0]
        cleaned_path = generate_relative_path(StorageEnvironment.CLEANED, self.ingestion_time, self.dataset.name)
        for cleaner in self.flow.cleaners:
            outputs = []
            for storage_object in paths:
                data = storage.find(storage_object.path)
                cleaned = cleaner.clean(data)
                path = storage.save(cleaned, f"{cleaned_path}/{extract_filename(storage_object.path)}")
                outputs.append(StorageObject("storage", path))
            paths = tuple(outputs)
        return paths

    def enrich(self, paths: tuple[StorageObject, ...]) -> tuple[StorageObject, ...]:
        storage = self.flow.storages[0]
        enriched_path = generate_relative_path(StorageEnvironment.ENRICHED, self.ingestion_time, self.dataset.name)
        for enricher in self.flow.enrichers:
            outputs = []
            for storage_object in paths:
                data = storage.find(storage_object.path)
                enriched = enricher.enrich(data)
                path = storage.save(
                    enriched,
                    f"{enriched_path}/{extract_filename(storage_object.path)}",
                )
                outputs.append(StorageObject("storage", path))
            paths = tuple(outputs)
        return paths

    def expose(self, paths: tuple[StorageObject, ...]) -> None:
        storage = self.flow.storages[0]
        for exposer in self.flow.exposers:
            for storage_object in paths:
                exposer.expose(storage.find(storage_object.path))

    def analyze(self, paths: tuple[StorageObject, ...]) -> None:
        storage = self.flow.storages[0]
        for analyzer in self.flow.analyzers:
            for storage_object in paths:
                analyzer.analyze(storage.find(storage_object.path))

    def cleanup(self) -> None:
        self.flow.after_pipeline(self)
