from dataset.definition import Audit, Dataframe, DatabaseConnection, Dataset, Destination, Datalake, DataWarehouse, Event, FileSource, Messaging, Source, StageDatabase
from pipeline.spark_based_streaming_pipeline import SparkStreamingPipeline


def build_dataset() -> Dataset:
    return Dataset(
        name="example",
        dataframe=Dataframe(schema=None, required_columns=frozenset()),
        event=Event(converter=lambda row: row),
        messaging=Messaging(topic="example-events", checkpoint_path="/tmp/checkpoint"),
        audit=Audit(),
        processors={
            "spark": type(
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
        given_pipeline = SparkStreamingPipeline(build_dataset())
        mocker.patch.object(given_pipeline, "publish_events", return_value=1)
        mock_start_batch_storage = mocker.patch.object(given_pipeline, "start_batch_storage")
        mock_start_batch_storage.return_value.awaitTermination = mocker.Mock()
        mocker.patch.object(given_pipeline, "populate_database")
        mocker.patch.object(given_pipeline, "populate_datawarehouse")
        mocker.patch.object(given_pipeline, "show_dataframe")
        mocker.patch.object(given_pipeline, "analyzing_via_spark")
        mocker.patch.object(given_pipeline, "analyzing_via_datawarehouse")
        mocker.patch("pipeline.spark_based_streaming_pipeline.log_line")
        mocker.patch.object(given_pipeline.spark, "stop")

        # When
        given_pipeline.run()

        # Then
        assert given_pipeline.publish_events.call_count == 1
        assert given_pipeline.start_batch_storage.call_count == 1
        assert mock_start_batch_storage.return_value.awaitTermination.call_count == 1
        assert given_pipeline.populate_database.call_count == 1
        assert given_pipeline.populate_datawarehouse.call_count == 1
        assert given_pipeline.show_dataframe.call_count == 1
        assert given_pipeline.analyzing_via_spark.call_count == 1
        assert given_pipeline.analyzing_via_datawarehouse.call_count == 1
        assert given_pipeline.spark.stop.call_count == 1
