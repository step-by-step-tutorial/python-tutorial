
CREATE TABLE IF NOT EXISTS customer
(
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    CONSTRAINT customer_name_country_unique UNIQUE (customer_name, country)
);

CREATE TABLE IF NOT EXISTS product
(
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    CONSTRAINT product_name_category_unique UNIQUE (product_name, category)
);

CREATE TABLE IF NOT EXISTS sale_order
(
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    CONSTRAINT sale_order_customer_fk
        FOREIGN KEY (customer_id)
        REFERENCES customer (customer_id)
);

CREATE TABLE IF NOT EXISTS order_item
(
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity NUMERIC(12, 2) NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    total_price NUMERIC(14, 2) NOT NULL,
    CONSTRAINT order_item_order_fk
        FOREIGN KEY (order_id)
        REFERENCES sale_order (order_id),
    CONSTRAINT order_item_product_fk
        FOREIGN KEY (product_id)
        REFERENCES product (product_id)
);

CREATE TABLE IF NOT EXISTS sale_stage
(
    order_id INTEGER NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    quantity NUMERIC(12, 2) NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    order_date DATE NOT NULL,
    country VARCHAR(100) NOT NULL,
    total_price NUMERIC(14, 2) NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL
);
