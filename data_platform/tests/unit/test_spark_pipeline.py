from data_platform.model import (
    AuditEndpoint,
    DataLakeEndpoint,
    DataWarehouseEndpoint,
    DataFrameModel,
    DatabaseEndpoint,
    Dataset,
    FileEndpoint,
    MessagingEndpoint,
)
from data_platform.pipeline.spark_pipeline import SparkPipeline


def build_dataset() -> Dataset:
    converter = type(
        "Converter",
        (),
        {
            "clean": lambda self, dataframe: dataframe,
            "enrich": lambda self, dataframe: dataframe,
        },
    )()
    analyzer = type("Analyzer", (), {"analyze": lambda self, dataframe: {}})()

    return Dataset(
        name="sale",
        dataframe=DataFrameModel(schema=None, required_columns=frozenset()),
        audit=AuditEndpoint(
            database_connection_name="audit.database",
            messaging_connection_name="audit.kafka.producer",
            datalake_connection_name="audit.datalake",
            create_sql_files={"create": "database/audit/create_tables.sql"},
            write_sql_files={"write": "database/audit/insert_event.sql"},
        ),
        transformers={"spark": converter},
        analyzers={"spark": analyzer, "datawarehouse": analyzer},
        endpoints={
            "sale.file.csv": FileEndpoint(file_name="sale.csv", file_path="resources/example.csv"),
            "sale.kafka.listener": MessagingEndpoint(connection_name="sale.kafka.listener", channel_name="example-events"),
            "sale.datalake": DataLakeEndpoint(connection_name="sale.datalake", bucket_name="bucket"),
            "sale.database": DatabaseEndpoint(
                connection_name="sale.database",
                schema="sale",
                stage_table_name="example_stage",
                full_stage_table_name="sale.example_stage",
                table_names=["sale.example_stage"],
            ),
            "sale.datawarehouse": DataWarehouseEndpoint(
                connection_name="sale.datawarehouse",
                schema="app_datawarehouse",
                table_name="example",
            ),
        },
    )


class TestRun:

    def test_should_execute_each_pipeline_step_once(self, mocker) -> None:
        given_audit_service = mocker.Mock()
        given_audit_service.start_pipeline.return_value = 10.0
        given_audit_service.start_task.side_effect = [
            ("task-1", 1.0),
            ("task-2", 2.0),
            ("task-3", 3.0),
            ("task-4", 4.0),
            ("task-5", 5.0),
            ("task-6", 6.0),
            ("task-7", 7.0),
            ("task-8", 8.0),
            ("task-9", 9.0),
            ("task-10", 10.0),
            ("task-11", 11.0),
        ] 

        mocker.patch("data_platform.pipeline.spark_pipeline.AuditService", return_value=given_audit_service)
        given_session = mocker.Mock()
        mocker.patch("data_platform.pipeline.spark_pipeline.create_session", return_value=given_session)
        given_pipeline = SparkPipeline(build_dataset())
        mock_ingest_raw_data = mocker.patch.object(given_pipeline, "ingest_raw_data", return_value="raw-data")
        mocker.patch.object(given_pipeline, "store_raw_data", return_value="raw")
        mock_clean = mocker.patch.object(given_pipeline, "clean", return_value="clean")
        mocker.patch.object(given_pipeline, "store_cleaned_data", return_value="clean-path")
        mock_enrich = mocker.patch.object(given_pipeline, "enrich", return_value="enriched")
        mocker.patch.object(given_pipeline, "store_enriched_data", return_value="enriched-path")
        mocker.patch.object(given_pipeline, "populate_enriched_data")
        mocker.patch.object(given_pipeline, "show_dataframe")
        mocker.patch.object(given_pipeline, "analyze_enriched_data")
        given_pipeline.run()

        assert mock_ingest_raw_data.call_count == 1
        assert given_pipeline.store_raw_data.call_count == 1
        assert mock_clean.call_count == 1
        assert given_pipeline.store_cleaned_data.call_count == 1
        assert mock_enrich.call_count == 1
        assert given_pipeline.store_enriched_data.call_count == 1
        assert given_pipeline.populate_enriched_data.call_count == 1
        assert given_pipeline.show_dataframe.call_count == 1
        assert given_pipeline.analyze_enriched_data.call_count == 1
        assert given_session.stop.call_count == 1
