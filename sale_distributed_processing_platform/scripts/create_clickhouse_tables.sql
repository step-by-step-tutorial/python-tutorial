
CREATE DATABASE IF NOT EXISTS sale_warehouse;

CREATE TABLE IF NOT EXISTS sale_warehouse.sale_fact
(
    order_id UInt32,
    customer_name String,
    product_name String,
    category String,
    country String,
    quantity Float64,
    unit_price Float64,
    total_price Float64,
    order_date Date,
    year UInt16,
    month UInt8
)
ENGINE = MergeTree()
ORDER BY (
    order_date,
    category,
    country,
    order_id
);
