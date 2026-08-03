CREATE DATABASE IF NOT EXISTS sale_warehouse;

CREATE TABLE IF NOT EXISTS sale_warehouse.sale_fact
(
    order_id UInt32,
    customer_name String,
    product_name String,
    category String,
    quantity Float64,
    unit_price Float64,
    order_date Date,
    country String,
    total_price Float64,
    year UInt16,
    month UInt8
)
    ENGINE = MergeTree()
    PARTITION BY toYYYYMM(order_date)
    ORDER BY
(
    order_date,
    country,
    category,
    order_id
);