CREATE SCHEMA IF NOT EXISTS online_shopping;
CREATE TABLE IF NOT EXISTS online_shopping.online_shopping_stage (
    order_id VARCHAR(64), order_date TIMESTAMP, sales_channel VARCHAR(100), country VARCHAR(100),
    product_name VARCHAR(250), unit_price NUMERIC, quantity NUMERIC, total_amount NUMERIC, net_revenue NUMERIC
);
