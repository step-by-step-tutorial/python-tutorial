from data_platform.model import AuditEndpoint, Dataset
from data_platform.pipeline.batch_pipeline import BatchPipeline


class _TestBatchPipeline(BatchPipeline):
    def __init__(self, dataset: Dataset, audit_service) -> None:
        super().__init__(dataset, audit_service=audit_service)
        self.pipeline_name = "test_pipeline"

    def ingest_raw_data(self):
        return "raw-data"

    def store_raw_data(self, raw_data) -> str:
        return "raw"

    def clean(self, raw_relative_path: str):
        return "clean"

    def store_cleaned_data(self, cleaned_data) -> str:
        return "clean-path"

    def enrich(self, cleaned_relative_path: str):
        return "enriched"

    def store_enriched_data(self, enriched_data) -> str:
        return "enriched-path"

    def populate_database(self, enriched_data_path: str) -> None:
        return None

    def populate_datawarehouse(self, enriched_data_path: str) -> None:
        return None

    def show_dataframe(self, enriched_data_path: str) -> None:
        return None

    def analyze_dataframe(self, enriched_data_path: str) -> None:
        return None

    def analyze_data_warehouse(self) -> None:
        return None


class TestBatchPipeline:

    def test_should_execute_the_shared_batch_workflow(self, mocker) -> None:
        given_audit_service = mocker.Mock()

        given_pipeline = _TestBatchPipeline(
            Dataset(
                "example",
                audit=AuditEndpoint(
                    database_connection_name="audit.database",
                    messaging_connection_name="audit.kafka.producer",
                    datalake_connection_name="audit.datalake",
                    create_sql_files={"create": "database/audit/create_tables.sql"},
                    write_sql_files={"write": "database/audit/insert_event.sql"},
                ),
            ),
            given_audit_service,
        )
        mocker.patch.object(given_pipeline, "ingest_raw_data", return_value="raw-data")
        mocker.patch.object(given_pipeline, "store_raw_data", return_value="raw")
        mocker.patch.object(given_pipeline, "clean", return_value="clean")
        mocker.patch.object(given_pipeline, "store_cleaned_data", return_value="clean-path")
        mocker.patch.object(given_pipeline, "enrich", return_value="enriched")
        mocker.patch.object(given_pipeline, "store_enriched_data", return_value="enriched-path")

        given_pipeline.run()

        assert given_audit_service.emit.call_count == 24

    def test_should_record_task_and_pipeline_failure(self, mocker) -> None:
        given_audit_service = mocker.Mock()

        given_pipeline = _TestBatchPipeline(
            Dataset(
                "example",
                audit=AuditEndpoint(
                    database_connection_name="audit.database",
                    messaging_connection_name="audit.kafka.producer",
                    datalake_connection_name="audit.datalake",
                    create_sql_files={"create": "database/audit/create_tables.sql"},
                    write_sql_files={"write": "database/audit/insert_event.sql"},
                ),
            ),
            given_audit_service,
        )
        mocker.patch.object(given_pipeline, "ingest_raw_data", return_value="raw-data")
        mocker.patch.object(given_pipeline, "store_raw_data", return_value="raw")
        mocker.patch.object(given_pipeline, "clean", side_effect=RuntimeError("boom"))

        try:
            given_pipeline.run()
        except RuntimeError:
            pass

        assert given_audit_service.emit.call_count == 8
