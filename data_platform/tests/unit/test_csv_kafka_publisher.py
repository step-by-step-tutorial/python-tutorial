from data_platform.model import FileEndpoint, MessagingEndpoint
from data_platform.service.csv_kafka_publisher import CsvKafkaPublisher
from data_platform.config.keys import Key
from data_platform.model.mapped_event import MappedEvent


class TestCsvKafkaPublisher:

    def test_should_read_csv_rows_and_publish_them_to_kafka(self, mocker) -> None:
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

        mock_read_csv = mocker.patch("data_platform.service.csv_kafka_publisher.read_csv_file", side_effect=_read_csv)
        given_event_converter = mocker.Mock()
        given_event_converter.map.side_effect = [
            MappedEvent(key="1", payload={"order_id": 1}),
            MappedEvent(key="2", payload={"order_id": 2}),
        ]
        given_producer = mocker.Mock()
        mock_ensure_topic = mocker.patch("data_platform.service.csv_kafka_publisher.ensure_topic_exists")

        actual = CsvKafkaPublisher(
            file_endpoint=given_file_endpoint,
            messaging_endpoint=given_messaging_endpoint,
            producer=given_producer,
            event_converter=given_event_converter,
        ).publish()

        assert actual == 2
        assert mock_read_csv.call_count == 1
        assert mock_read_csv.call_args.args[0] == "/tmp/sale.csv"
        assert mock_ensure_topic.call_count == 1
        assert mock_ensure_topic.call_args.args == ("localhost:9092", "sale-events")
        assert given_producer.produce.call_count == 2
        assert given_producer.produce.call_args_list[0].kwargs["topic"] == "sale-events"
        assert given_producer.produce.call_args_list[0].kwargs["key"] == b"1"
        assert given_producer.produce.call_args_list[1].kwargs["key"] == b"2"
        assert given_producer.poll.call_count == 1
        assert given_producer.flush.call_count == 1

    def test_should_publish_a_single_row(self, mocker) -> None:
        given_file_endpoint = FileEndpoint(name="sale.file.csv", file_path="/tmp/sale.csv")
        given_messaging_endpoint = MessagingEndpoint(
            connection_name="sale.kafka.producer",
            channel_name="sale-events",
            bootstrap_servers="localhost:9092",
        )
        given_producer = mocker.Mock()
        given_event_converter = mocker.Mock()
        given_event_converter.map.return_value = MappedEvent(key="1", payload={"order_id": 1})

        publisher = CsvKafkaPublisher(
            file_endpoint=given_file_endpoint,
            messaging_endpoint=given_messaging_endpoint,
            producer=given_producer,
            event_converter=given_event_converter,
        )

        publisher.publish_event({"order_id": "1"})

        assert given_producer.produce.call_count == 1
        assert given_producer.produce.call_args.kwargs["topic"] == "sale-events"


