from ml_prediction.features.feature_model import FeatureModel


class OnlineShoppingFeatureModel(FeatureModel):
    numeric_features = (
        "order_id", "customer_id", "unit_price", "quantity", "subtotal",
        "discount_percent", "shipping_cost", "tax_amount", "total_amount", "delivery_days",
    )
    boolean_features = ()
    categorical_features = (
        "order_date", "sales_channel", "first_name", "last_name", "email", "phone",
        "shipping_address", "country", "currency", "warehouse", "product_name", "category",
        "payment_status", "fulfillment_status", "estimated_delivery_date", "coupon_code",
        "payment_method", "shipping_method",
    )

    def get_numeric_features(self) -> tuple[str, ...]:
        return self.numeric_features

    def get_boolean_features(self) -> tuple[str, ...]:
        return self.boolean_features

    def get_categorical_features(self) -> tuple[str, ...]:
        return self.categorical_features
