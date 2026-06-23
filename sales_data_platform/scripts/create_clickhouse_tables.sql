CREATE DATABASE IF NOT EXISTS sales_warehouse;

CREATE TABLE IF NOT EXISTS sales_warehouse.fact_sales
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
ORDER BY (order_date, category, country);