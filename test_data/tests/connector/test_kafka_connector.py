from test_data.connector import kafka_connector


def test_create_producer_uses_kafka_defaults(mocker) -> None:
    producer = mocker.patch("test_data.connector.kafka_connector.Producer")

    kafka_connector.create_producer()

    assert producer.call_args.args[0] == {
        "bootstrap.servers": kafka_connector.env_config.KAFKA_BOOTSTRAP_SERVERS,
        "enable.idempotence": True,
        "acks": "all",
        "retries": 1,
        "message.timeout.ms": 5_000,
        "delivery.timeout.ms": 5_000,
        "socket.timeout.ms": 2_000,
        "linger.ms": 10,
        "log_level": 0,
    }
