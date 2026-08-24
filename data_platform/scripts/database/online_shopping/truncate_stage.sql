CREATE SCHEMA IF NOT EXISTS online_shopping;
CREATE TABLE IF NOT EXISTS online_shopping.online_shopping_stage (
    order_id BIGINT, order_date TIMESTAMP, sales_channel VARCHAR(100), customer_id BIGINT,
    first_name VARCHAR(100), last_name VARCHAR(100), email VARCHAR(250), phone VARCHAR(64),
    shipping_address VARCHAR(500), country VARCHAR(100), currency VARCHAR(16), warehouse VARCHAR(250),
    product_name VARCHAR(250), category VARCHAR(100), unit_price NUMERIC, quantity NUMERIC,
    subtotal NUMERIC, discount_percent NUMERIC, shipping_cost NUMERIC, tax_amount NUMERIC,
    total_amount NUMERIC, payment_status VARCHAR(64), fulfillment_status VARCHAR(64),
    estimated_delivery_date TIMESTAMP, coupon_code VARCHAR(64), payment_method VARCHAR(100),
    shipping_method VARCHAR(100), delivery_days NUMERIC, order_status VARCHAR(64),
    discount_amount NUMERIC, net_revenue NUMERIC, year INTEGER, month INTEGER
);
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS customer_id BIGINT;
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS email VARCHAR(250);
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS phone VARCHAR(64);
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS shipping_address VARCHAR(500);
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS currency VARCHAR(16);
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS warehouse VARCHAR(250);
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS category VARCHAR(100);
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS subtotal NUMERIC;
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS discount_percent NUMERIC;
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS shipping_cost NUMERIC;
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS tax_amount NUMERIC;
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS payment_status VARCHAR(64);
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS fulfillment_status VARCHAR(64);
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS estimated_delivery_date TIMESTAMP;
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS coupon_code VARCHAR(64);
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS payment_method VARCHAR(100);
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS shipping_method VARCHAR(100);
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS delivery_days NUMERIC;
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS order_status VARCHAR(64);
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS discount_amount NUMERIC;
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS year INTEGER;
ALTER TABLE online_shopping.online_shopping_stage ADD COLUMN IF NOT EXISTS month INTEGER;
TRUNCATE TABLE online_shopping.online_shopping_stage;
