import pytest

from service.messaging.event_publisher import EventPublisher
from transformation.conversion.event_mapper import MappedEvent

pytestmark = pytest.mark.unit


class TestEventPublisher:

    def test_should_publish_a_prepared_event(self, mocker) -> None:
        given_producer = mocker.Mock()
        given_message = MappedEvent(key="1", payload={"order_id": 1, "customer_name": "Ali Ahmadi"})

        EventPublisher(producer=given_producer).publish("sale-events", given_message)

        assert given_producer.produce.call_count == 1
        kwargs = given_producer.produce.call_args.kwargs
        assert kwargs["topic"] == "sale-events"
        assert kwargs["key"] == b"1"
        assert kwargs["value"] == b'{"order_id": 1, "customer_name": "Ali Ahmadi"}'

    def test_should_publish_many_prepared_events_and_flush(self, mocker) -> None:
        given_producer = mocker.Mock()
        given_messages = (
            MappedEvent(key="1", payload={"order_id": 1}),
            MappedEvent(key="2", payload={"order_id": 2}),
        )

        actual = EventPublisher(producer=given_producer).publish_many("sale-events", given_messages)

        assert actual == 2
        assert given_producer.produce.call_count == 2
        assert given_producer.poll.call_count == 1
        assert given_producer.flush.call_count == 1
