from data_platform.model import FileEndpoint, MessagingEndpoint
from data_platform.service.csv_kafka_publisher import CsvKafkaPublisher


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
        given_producer = mocker.Mock()
        mock_ensure_topic = mocker.patch("data_platform.service.csv_kafka_publisher.ensure_topic_exists")
        mocker.patch("data_platform.service.csv_kafka_publisher.connection_registry.get_item", return_value=given_producer)

        actual = CsvKafkaPublisher(
            file_endpoint=given_file_endpoint,
            messaging_endpoint=given_messaging_endpoint,
        ).publish()

        assert actual == 2
        assert mock_read_csv.call_count == 1
        assert mock_read_csv.call_args.args[0] == "/tmp/sale.csv"
        assert mock_ensure_topic.call_count == 1
        assert mock_ensure_topic.call_args.args == ("localhost:9092", "sale-events")
        assert given_producer.produce.call_count == 2
        assert given_producer.produce.call_args_list[0].kwargs["topic"] == "sale-events"
        assert given_producer.poll.call_count == 1
        assert given_producer.flush.call_count == 1

