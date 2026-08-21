from confluent_kafka import KafkaError

from kafka_utils import handle_delivery


def test_handle_delivery_ignores_successful_delivery() -> None:
    handle_delivery(None, None)


def test_handle_delivery_logs_delivery_error(caplog) -> None:
    error = KafkaError(KafkaError._MSG_TIMED_OUT)

    handle_delivery(error, None)

    assert "Kafka message delivery failed" in caplog.text
