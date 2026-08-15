from service.messaging.event_publisher import EventPublisher
from dataset.sale.config import SALE_DATASET
from dataset.sale.columns import SALE_COLUMNS


class TestEventPublisher:

    def test_should_publish_a_single_row_as_event(self, mocker) -> None:
        given_producer = mocker.Mock()
        given_row = {
            SALE_COLUMNS.ORDER_ID: "1",
            SALE_COLUMNS.CUSTOMER_NAME: "Ali Ahmadi",
            SALE_COLUMNS.PRODUCT_NAME: "Laptop",
            SALE_COLUMNS.CATEGORY: "Electronics",
            SALE_COLUMNS.QUANTITY: "2",
            SALE_COLUMNS.UNIT_PRICE: "1000",
            SALE_COLUMNS.ORDER_DATE: "2026-01-10",
            SALE_COLUMNS.COUNTRY: "Iran",
        }

        EventPublisher(producer=given_producer).publish_row_as_event(given_row, SALE_DATASET)

        assert given_producer.produce.call_count == 1
        kwargs = given_producer.produce.call_args.kwargs
        assert kwargs["topic"] == "sale-events"
        assert kwargs["key"] == "1"

    def test_should_publish_rows_from_csv_and_flush_producer(self, mocker) -> None:
        given_producer = mocker.Mock()

        def given_read_csv_file(path_str, consumer):
            consumer(
                {
                    SALE_COLUMNS.ORDER_ID: "1",
                    SALE_COLUMNS.CUSTOMER_NAME: "Ali Ahmadi",
                    SALE_COLUMNS.PRODUCT_NAME: "Laptop",
                    SALE_COLUMNS.CATEGORY: "Electronics",
                    SALE_COLUMNS.QUANTITY: "2",
                    SALE_COLUMNS.UNIT_PRICE: "1000",
                    SALE_COLUMNS.ORDER_DATE: "2026-01-10",
                    SALE_COLUMNS.COUNTRY: "Iran",
                }
            )
            return 1

        mocker.patch("service.messaging.event_publisher.read_csv_file", side_effect=given_read_csv_file)

        actual = EventPublisher(producer=given_producer).publish_csv("resources/sale.csv", SALE_DATASET)

        assert actual == 1
        assert given_producer.poll.call_count == 1
        assert given_producer.flush.call_count == 1
        assert given_producer.produce.call_count == 1
