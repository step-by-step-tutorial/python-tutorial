from dataset.definition import Audit, Dataframe, DatabaseConnection, Dataset, Destination, Datalake, DataWarehouse, FileSource, Messaging, Serialization, Source, StageDatabase
from pipeline.inmemory_pipeline import InmemoryPipeline


def build_dataset() -> Dataset:
    return Dataset(
        name="example",
        dataframe=Dataframe(schema=None, required_columns=frozenset()),
        serialization=Serialization(event_converter=lambda row: row),
        messaging=Messaging(topic="example-events"),
        audit=Audit(),
        processors={
            "inmemory": type(
                "Processor",
                (),
                {
                    "clean": lambda self, dataframe: dataframe,
                    "enrich": lambda self, dataframe: dataframe,
                    "analyze": lambda self, dataframe: {},
                },
            )()
        },
        source=Source(file=FileSource(file_name="example.csv", file_path="resources/example.csv")),
        destination=Destination(
            datalake=Datalake(bucket_name="bucket"),
            database=StageDatabase(connection=DatabaseConnection(), table_name="sale.example_stage"),
            datawarehouse=DataWarehouse(full_table_name="app_datawarehouse.example"),
        ),
    )


class TestRun:

    def test_should_execute_each_pipeline_step_once(self, mocker) -> None:
        # Given
        given_pipeline = InmemoryPipeline(build_dataset())
        mocker.patch.object(given_pipeline, "store_raw_data", return_value="raw")
        mocker.patch.object(given_pipeline, "cleaning", return_value="clean")
        mocker.patch.object(given_pipeline, "enriching", return_value="enriched")
        mocker.patch.object(given_pipeline, "populate_database")
        mocker.patch.object(given_pipeline, "populate_datawarehouse")
        mocker.patch.object(given_pipeline, "show_dataframe")
        mocker.patch.object(given_pipeline, "analyzing_via_memory")
        mocker.patch.object(given_pipeline, "analyzing_via_datawarehouse")
        mocker.patch("pipeline.inmemory_pipeline.log_line")

        # When
        given_pipeline.run()

        # Then
        assert given_pipeline.store_raw_data.call_count == 1
        assert given_pipeline.cleaning.call_count == 1
        assert given_pipeline.enriching.call_count == 1
        assert given_pipeline.populate_database.call_count == 1
        assert given_pipeline.populate_datawarehouse.call_count == 1
        assert given_pipeline.show_dataframe.call_count == 1
        assert given_pipeline.analyzing_via_memory.call_count == 1
        assert given_pipeline.analyzing_via_datawarehouse.call_count == 1
