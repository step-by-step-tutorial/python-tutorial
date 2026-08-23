from data_platform.model import Dataset, FileEndpoint, MessagingEndpoint
from data_platform.dataset.shared_endpoints import AUDIT_ENDPOINT
from data_platform.service.csv_publisher_service import CsvPublisherService
from data_platform.keys import Key
from data_platform.transformer.event_transformer import MappedEvent


class TestCsvPublisherService:

    def test_should_read_csv_rows_and_publish_them_to_kafka(self, mocker) -> None:
        given_dataset = Dataset(name="sale", audit=AUDIT_ENDPOINT)
        given_file_endpoint = FileEndpoint(name="sale.file.csv", file_path="/tmp/sale.csv")
        given_messaging_endpoint = MessagingEndpoint(
            connection_name="sale.kafka.producer",
            channel_name="sale-events",
            bootstrap_servers="localhost:9092",
        )

        def _read_csv(path, consumer):
            consumer({"order_id": "1"})
            consumer({"order_id": "2"})
            return 2

        mock_read_csv = mocker.patch("data_platform.service.csv_publisher_service.read_csv_file", side_effect=_read_csv)
        mock_mapper = mocker.patch("data_platform.service.csv_publisher_service.get_event_transformer")
        mock_mapper.return_value.map.side_effect = [
            MappedEvent(key="1", payload={"order_id": 1}),
            MappedEvent(key="2", payload={"order_id": 2}),
        ]
        mock_get_connection = mocker.patch("data_platform.service.csv_publisher_service.get_connection")
        given_producer = mocker.Mock()
        mock_get_connection.return_value = given_producer
        mock_ensure_topic = mocker.patch("data_platform.service.csv_publisher_service.ensure_topic_exists")

        actual = CsvPublisherService(
            dataset=given_dataset,
            file_endpoint=given_file_endpoint,
            messaging_endpoint=given_messaging_endpoint,
        ).publish_data()

        assert actual == 2
        assert mock_read_csv.call_count == 1
        assert mock_read_csv.call_args.args[0] == "/tmp/sale.csv"
        assert mock_mapper.call_count == 1
        assert mock_mapper.call_args.args == ("sale",)
        assert mock_get_connection.call_count == 1
        assert mock_get_connection.call_args.args == (Key.SALE_KAFKA_PRODUCER,)
        assert mock_ensure_topic.call_count == 1
        assert mock_ensure_topic.call_args.args == ("localhost:9092", "sale-events")
        assert given_producer.produce.call_count == 2
        assert given_producer.produce.call_args_list[0].kwargs["topic"] == "sale-events"
        assert given_producer.produce.call_args_list[0].kwargs["key"] == b"1"
        assert given_producer.produce.call_args_list[1].kwargs["key"] == b"2"
        assert given_producer.poll.call_count == 1
        assert given_producer.flush.call_count == 1

    def test_should_publish_a_single_row(self, mocker) -> None:
        given_dataset = Dataset(name="sale", audit=AUDIT_ENDPOINT)
        given_file_endpoint = FileEndpoint(name="sale.file.csv", file_path="/tmp/sale.csv")
        given_messaging_endpoint = MessagingEndpoint(
            connection_name="sale.kafka.producer",
            channel_name="sale-events",
            bootstrap_servers="localhost:9092",
        )
        mock_mapper = mocker.patch("data_platform.service.csv_publisher_service.get_event_transformer")
        mock_mapper.return_value.map.return_value = MappedEvent(key="1", payload={"order_id": 1})
        mock_get_connection = mocker.patch("data_platform.service.csv_publisher_service.get_connection")
        given_producer = mocker.Mock()
        mock_get_connection.return_value = given_producer

        publisher = CsvPublisherService(
            dataset=given_dataset,
            file_endpoint=given_file_endpoint,
            messaging_endpoint=given_messaging_endpoint,
        )

        publisher.publish_event({"order_id": "1"})

        assert given_producer.produce.call_count == 1
        assert given_producer.produce.call_args.kwargs["topic"] == "sale-events"
