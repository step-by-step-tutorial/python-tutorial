from data_platform.pipeline.batch_pipeline import BatchPipeline
from data_platform.adapter.dag_pipeline_adapter import DagPipelineAdapter


class TestDagPipelineAdapter:
    def test_should_ingest_and_store_raw_data(self, mocker) -> None:
        pipeline = mocker.Mock(spec=BatchPipeline)
        pipeline.ingest_raw_data.return_value = "raw-data"
        pipeline.store_raw_data.return_value = "raw/path"

        result = DagPipelineAdapter(pipeline).ingest_raw_data()

        assert result == "raw/path"
        pipeline.store_raw_data.assert_called_once_with("raw-data")

    def test_should_clean_and_store_data(self, mocker) -> None:
        pipeline = mocker.Mock(spec=BatchPipeline)
        pipeline.cleaning.return_value = "cleaned-data"
        pipeline.store_cleaned_data.return_value = "cleaned/path"

        result = DagPipelineAdapter(pipeline).cleaning("raw/path")

        assert result == "cleaned/path"
        pipeline.cleaning.assert_called_once_with("raw/path")
        pipeline.store_cleaned_data.assert_called_once_with("cleaned-data")

    def test_should_enrich_and_store_data(self, mocker) -> None:
        pipeline = mocker.Mock(spec=BatchPipeline)
        pipeline.enriching.return_value = "enriched-data"
        pipeline.store_enriched_data.return_value = "enriched/path"

        result = DagPipelineAdapter(pipeline).enriching("cleaned/path")

        assert result == "enriched/path"
        pipeline.enriching.assert_called_once_with("cleaned/path")
        pipeline.store_enriched_data.assert_called_once_with("enriched-data")
