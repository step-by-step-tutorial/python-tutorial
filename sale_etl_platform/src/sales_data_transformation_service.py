import pandas as pd


class SalesDataTransformationService:
    def transform_sales_data(
            self,
            cleaned_sales_dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        transformed_sales_dataframe = cleaned_sales_dataframe.copy()

        transformed_sales_dataframe["total_price"] = (
                transformed_sales_dataframe["quantity"]
                * transformed_sales_dataframe["unit_price"]
        )

        transformed_sales_dataframe["year"] = transformed_sales_dataframe[
            "order_date"
        ].dt.year

        transformed_sales_dataframe["month"] = transformed_sales_dataframe[
            "order_date"
        ].dt.month

        return transformed_sales_dataframe

    def build_sales_warehouse_dataframe(
            self,
            transformed_sales_dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        sales_warehouse_dataframe = transformed_sales_dataframe.rename(
            columns={"product": "product_name"}
        ).copy()

        sales_warehouse_dataframe = sales_warehouse_dataframe[
            [
                "order_id",
                "customer_name",
                "product_name",
                "category",
                "country",
                "quantity",
                "unit_price",
                "total_price",
                "order_date",
                "year",
                "month",
            ]
        ]

        sales_warehouse_dataframe["order_date"] = sales_warehouse_dataframe[
            "order_date"
        ].dt.date

        return sales_warehouse_dataframe