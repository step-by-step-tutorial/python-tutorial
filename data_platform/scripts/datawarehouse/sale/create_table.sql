CREATE TABLE IF NOT EXISTS app_datawarehouse.sale_table
(
    order_id
    Int64,
    customer_name
    String,
    product_name
    String,
    category
    String,
    quantity
    Float64,
    unit_price
    Float64,
    order_date
    Date,
    country
    String,
    total_price
    Float64,
    year
    UInt16,
    month
    UInt8
)
    ENGINE = MergeTree
(
)
    PARTITION BY toYYYYMM
(
    order_date
)
    ORDER BY
(
    order_date,
    country,
    category,
    order_id
)
