from streaming.csv_publisher import CsvPublisher
from dataset.sale.config import SALE_DATASET
from dataset.sale.model import SALE_COLUMNS


class TestCsvPublisher:

    def test_should_publish_events_from_csv(self, mocker) -> None:
        # Given
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

        mock_create_streaming_producer = mocker.patch(
            "streaming.csv_publisher.create_streaming_producer",
            return_value=given_producer,
        )
        mock_read_csv_file = mocker.patch(
            "streaming.csv_publisher.read_csv_file",
            side_effect=given_read_csv_file,
        )

        # When
        actual = CsvPublisher().publish(SALE_DATASET)

        # Then
        assert actual == 1
        assert mock_create_streaming_producer.call_count == 1
        assert mock_read_csv_file.call_count == 1
        assert given_producer.poll.call_count == 1
        assert given_producer.flush.call_count == 1
        assert given_producer.produce.call_count == 1

    def test_should_publish_a_single_row_as_event(self, mocker) -> None:
        # Given
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

        # When
        CsvPublisher.publish_row_as_event(given_row, SALE_DATASET, given_producer)

        # Then
        assert given_producer.produce.call_count == 1
