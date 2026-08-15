from dataset.definition import (
    Audit,
    DataLakeEndpoint,
    DataWarehouseEndpoint,
    Dataframe,
    DatabaseEndpoint,
    Dataset,
    Event,
    FileEndpoint,
    MessagingEndpoint,
)
from pipeline.inmemory_pipeline import InmemoryPipeline


def build_dataset() -> Dataset:
    processor = type(
        "Processor",
        (),
        {
            "clean": lambda self, dataframe: dataframe,
            "enrich": lambda self, dataframe: dataframe,
            "analyze": lambda self, dataframe: {},
        },
    )()

    return Dataset(
        name="example",
        dataframe=Dataframe(schema=None, required_columns=frozenset()),
        event=Event(),
        audit=Audit(),
        processor_factories={"inmemory": lambda: processor},
        sources={
            "file": FileEndpoint(file_name="example.csv", file_path="resources/example.csv"),
            "messaging": MessagingEndpoint(topic="example-events"),
        },
        destinations={
            "datalake": DataLakeEndpoint(bucket_name="bucket"),
            "database": DatabaseEndpoint(table_name="sale.example_stage"),
            "datawarehouse": DataWarehouseEndpoint(full_table_name="app_datawarehouse.example"),
        },
    )


class TestRun:

    def test_should_execute_each_pipeline_step_once(self, mocker) -> None:
        given_pipeline = InmemoryPipeline(build_dataset())
        mocker.patch.object(given_pipeline, "store_raw_data", return_value="raw")
        mocker.patch.object(given_pipeline, "cleaning", return_value="clean")
        mocker.patch.object(given_pipeline, "enriching", return_value="enriched")
        mocker.patch.object(given_pipeline, "populate_database")
        mocker.patch.object(given_pipeline, "populate_datawarehouse")
        mocker.patch.object(given_pipeline, "show_dataframe")
        mocker.patch.object(given_pipeline, "analyze_primary")
        mocker.patch.object(given_pipeline, "analyzing_via_datawarehouse")
        mocker.patch("pipeline.inmemory_pipeline.log_line")

        given_pipeline.run()

        assert given_pipeline.store_raw_data.call_count == 1
        assert given_pipeline.cleaning.call_count == 1
        assert given_pipeline.enriching.call_count == 1
        assert given_pipeline.populate_database.call_count == 1
        assert given_pipeline.populate_datawarehouse.call_count == 1
        assert given_pipeline.show_dataframe.call_count == 1
        assert given_pipeline.analyze_primary.call_count == 1
        assert given_pipeline.analyzing_via_datawarehouse.call_count == 1
