from data_platform.model import Dataset, StorageObject
from data_platform.pipeline.pipeline import Pipeline
from data_platform.util.path_utils import extract_filename


class ConfiguredPipeline(Pipeline):

    def __init__(self, dataset: Dataset) -> None:
        super().__init__(dataset)
        self.definition = dataset.pipeline_steps

    def prepare(self) -> None:
        self.definition.before_pipeline(self)

    def ingest(self) -> tuple[StorageObject, ...]:
        storage = self.definition.storages[0]
        storage_objects = []
        for ingestor in self.definition.ingestors:
            data = ingestor.ingest()
            path = storage.save(
                data, f"{self.storage_relative_path}/{ingestor.name}"
            )
            storage_objects.append(StorageObject("storage", path))
        return tuple(storage_objects)

    def clean(self, paths: tuple[StorageObject, ...]) -> tuple[StorageObject, ...]:
        storage = self.definition.storages[0]
        for index, cleaner in enumerate(self.definition.cleaners, start=1):
            outputs = []
            for storage_object in paths:
                data = storage.find(storage_object.path)
                cleaned = cleaner.clean(data)
                path = storage.save(
                    cleaned,
                    f"{self.storage_relative_path}/cleaned/step_{index}/{extract_filename(storage_object.path)}",
                )
                outputs.append(StorageObject("storage", path))
            paths = tuple(outputs)
        return paths

    def enrich(self, paths: tuple[StorageObject, ...]) -> tuple[StorageObject, ...]:
        storage = self.definition.storages[0]
        for index, enricher in enumerate(self.definition.enrichers, start=1):
            outputs = []
            for storage_object in paths:
                data = storage.find(storage_object.path)
                enriched = enricher.enrich(data)
                path = storage.save(
                    enriched,
                    f"{self.storage_relative_path}/enriched/step_{index}/{extract_filename(storage_object.path)}",
                )
                outputs.append(StorageObject("storage", path))
            paths = tuple(outputs)
        return paths

    def expose(self, paths: tuple[StorageObject, ...]) -> None:
        storage = self.definition.storages[0]
        for exposer in self.definition.exposers:
            for storage_object in paths:
                exposer.expose(storage.find(storage_object.path))

    def analyze(self, paths: tuple[StorageObject, ...]) -> None:
        storage = self.definition.storages[0]
        for analyzer in self.definition.analyzers:
            for storage_object in paths:
                analyzer.analyze(storage.find(storage_object.path))

    def cleanup(self) -> None:
        self.definition.after_pipeline(self)

