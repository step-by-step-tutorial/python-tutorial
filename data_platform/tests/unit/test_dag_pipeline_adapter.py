from data_platform.pipeline.batch_pipeline import BatchPipeline
from data_platform.adapter.dag_pipeline_adapter import DagPipelineAdapter


class TestDagPipelineAdapter:
    def test_should_prepare_pipeline(self, mocker) -> None:
        pipeline = mocker.Mock(spec=BatchPipeline)

        DagPipelineAdapter(pipeline).prepare()

        pipeline.before_run.assert_called_once()

    def test_should_ingest_and_store_raw_data(self, mocker) -> None:
        pipeline = mocker.Mock(spec=BatchPipeline)
        pipeline.ingest_raw_data.return_value = "raw-data"
        pipeline.store_raw_data.return_value = "raw/path"

        result = DagPipelineAdapter(pipeline).ingest_raw_data()

        assert result == "raw/path"
        pipeline.store_raw_data.assert_called_once_with("raw-data")

    def test_should_clean_and_store_data(self, mocker) -> None:
        pipeline = mocker.Mock(spec=BatchPipeline)
        pipeline.clean.return_value = "cleaned-data"
        pipeline.store_cleaned_data.return_value = "cleaned/path"

        result = DagPipelineAdapter(pipeline).clean("raw/path")

        assert result == "cleaned/path"
        pipeline.clean.assert_called_once_with("raw/path")
        pipeline.store_cleaned_data.assert_called_once_with("cleaned-data")

    def test_should_enrich_and_store_data(self, mocker) -> None:
        pipeline = mocker.Mock(spec=BatchPipeline)
        pipeline.enrich.return_value = "enriched-data"
        pipeline.store_enriched_data.return_value = "enriched/path"

        result = DagPipelineAdapter(pipeline).enrich("cleaned/path")

        assert result == "enriched/path"
        pipeline.enrich.assert_called_once_with("cleaned/path")
        pipeline.store_enriched_data.assert_called_once_with("enriched-data")

    def test_should_clean_up_pipeline(self, mocker) -> None:
        pipeline = mocker.Mock(spec=BatchPipeline)

        DagPipelineAdapter(pipeline).clean_up()

        pipeline.after_run.assert_called_once()
