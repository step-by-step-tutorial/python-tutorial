CREATE TABLE IF NOT EXISTS app_warehouse.online_shopping_table (
    order_id String, order_date DateTime, sales_channel String, country String, product_name String,
    unit_price Float64, quantity Float64, total_amount Float64, net_revenue Float64
) ENGINE = MergeTree() ORDER BY order_id;
