from data_platform.config.keys import Key
from data_platform.domain.online_shopping.dataset import ONLINE_SHOPPING_DATASET
from data_platform.ingestion.rest_api_csv_ingestor import RestApiCsvIngestor
from data_platform.model import RestApiEndpoint
from data_platform.registry.ingestor_registry import ingestor_registry


def register_online_shopping_ingestors() -> None:
    if ingestor_registry.contains(Key.ONLINE_SHOPPING_REST_API):
        return

    ingestor = RestApiCsvIngestor(ONLINE_SHOPPING_DATASET.get_endpoint(Key.ONLINE_SHOPPING_REST_API, RestApiEndpoint))
    ingestor_registry.register(Key.ONLINE_SHOPPING_REST_API, ingestor)
