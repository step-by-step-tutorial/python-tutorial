from dataset.definition import DatabaseConnection, Dataset, Destination, Datalake, DataWarehouse, FileSource, Source, StageDatabase, Streaming
from pipeline.spark_based_pipeline import SparkPipeline


def build_dataset() -> Dataset:
    return Dataset(
        name="example",
        dataframe_schema=None,
        required_columns=frozenset(),
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
        event_converter=lambda row: row,
        source=Source(file=FileSource(file_name="example.csv", file_path="resources/example.csv")),
        destination=Destination(
            datalake=Datalake(bucket_name="bucket"),
            database=StageDatabase(connection=DatabaseConnection(), table_name="sale.example_stage"),
            datawarehouse=DataWarehouse(full_table_name="app_datawarehouse.example"),
        ),
        streaming=Streaming(topic="example-events"),
    )


class TestRun:

    def test_should_execute_each_pipeline_step_once(self, mocker) -> None:
        # Given
        given_pipeline = SparkPipeline(build_dataset())
        mocker.patch.object(given_pipeline, "store_raw_data", return_value="raw")
        mocker.patch.object(given_pipeline, "cleaning", return_value="clean")
        mocker.patch.object(given_pipeline, "enriching", return_value="enriched")
        mocker.patch.object(given_pipeline, "populate_database")
        mocker.patch.object(given_pipeline, "populate_datawarehouse")
        mocker.patch.object(given_pipeline, "show_dataframe")
        mocker.patch.object(given_pipeline, "analyzing_via_spark")
        mocker.patch.object(given_pipeline, "analyzing_via_datawarehouse")
        mocker.patch("pipeline.spark_based_pipeline.log_line")
        mocker.patch.object(given_pipeline.spark, "stop")

        # When
        given_pipeline.run()

        # Then
        assert given_pipeline.store_raw_data.call_count == 1
        assert given_pipeline.cleaning.call_count == 1
        assert given_pipeline.enriching.call_count == 1
        assert given_pipeline.populate_database.call_count == 1
        assert given_pipeline.populate_datawarehouse.call_count == 1
        assert given_pipeline.show_dataframe.call_count == 1
        assert given_pipeline.analyzing_via_spark.call_count == 1
        assert given_pipeline.analyzing_via_datawarehouse.call_count == 1
        assert given_pipeline.spark.stop.call_count == 1
