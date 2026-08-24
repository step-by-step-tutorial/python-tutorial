import pandas as pd

from data_platform.domain.online_shopping.inmemory_transformer import InmemoryOnlineShoppingTransformer


class TestInmemoryOnlineShoppingTransformer:
    def test_should_clean_and_enrich_downloaded_orders(self) -> None:
        raw_data = pd.DataFrame(
            {
                "order_id": [1, 1, 2],
                "order_date": ["2026-01-01", "2026-01-01", "invalid"],
                "customer_id": [10, 10, 11],
                "sales_channel": ["web", "web", "web"],
                "country": ["DE", "DE", "DE"],
                "product_name": ["Book", "Book", "Pen"],
                "unit_price": ["10", "10", "5"],
                "quantity": ["2", "2", "1"],
                "subtotal": ["20", "20", "5"],
                "discount_percent": ["10", "10", "0"],
                "shipping_cost": ["5", "5", "5"],
                "tax_amount": ["2", "2", "0.5"],
                "total_amount": ["25", "25", "10.5"],
                "estimated_delivery_date": ["2026-01-03", "2026-01-03", "2026-01-05"],
                "delivery_days": ["2", "2", "1"],
                "order_status": ["delivered", "delivered", "delivered"],
            }
        )

        cleaned_data = InmemoryOnlineShoppingTransformer().clean(raw_data)
        actual = InmemoryOnlineShoppingTransformer().enrich(cleaned_data)

        assert actual.to_dict("records")[0]["discount_amount"] == 2.0
        assert actual.to_dict("records")[0]["net_revenue"] == 25.0
        assert actual.to_dict("records")[0]["year"] == 2026


