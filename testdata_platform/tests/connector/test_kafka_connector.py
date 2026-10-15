import pytest

from testdata_platform.connector import kafka_connector


def test_create_producer_uses_kafka_defaults(mocker) -> None:
    producer = mocker.patch("testdata_platform.connector.kafka_connector.Producer")

    kafka_connector.create_producer("kafka:29092")

    assert producer.call_args.args[0] == {
        "bootstrap.servers": "kafka:29092",
        "enable.idempotence": True,
        "acks": "all",
        "retries": 1,
        "message.timeout.ms": 5_000,
        "delivery.timeout.ms": 5_000,
        "socket.timeout.ms": 2_000,
        "linger.ms": 10,
        "log_level": 0,
    }


def test_publish_sends_rows_keyed_by_column_and_flushes(mocker) -> None:
    producer = mocker.patch("testdata_platform.connector.kafka_connector.create_producer").return_value
    producer.flush.return_value = 0

    kafka_connector.publish("kafka:29092", "events", [{"id": "1", "name": "Zoë"}], "id", 2.0)

    assert producer.produce.call_args.kwargs["key"] == "1"
    assert producer.produce.call_args.kwargs["value"] == '{"id": "1", "name": "Zoë"}'.encode("utf-8")
    producer.flush.assert_called_once_with(2.0)


def test_publish_raises_when_messages_stay_pending(mocker) -> None:
    producer = mocker.patch("testdata_platform.connector.kafka_connector.create_producer").return_value
    producer.flush.return_value = 3

    with pytest.raises(RuntimeError, match="3 messages still pending"):
        kafka_connector.publish("kafka:29092", "events", [{"id": "1"}], "id", 2.0)
