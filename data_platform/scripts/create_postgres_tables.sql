CREATE SCHEMA IF NOT EXISTS audit;

CREATE SCHEMA IF NOT EXISTS sale;

CREATE TABLE IF NOT EXISTS customer (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(200) NOT NULL,
    country VARCHAR(100) NOT NULL,

    CONSTRAINT customer_name_country_unique
    UNIQUE (customer_name, country)
);

CREATE TABLE IF NOT EXISTS product (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,

    CONSTRAINT product_name_category_unique
    UNIQUE (product_name, category)
);

CREATE TABLE IF NOT EXISTS sale_order (
    order_id BIGINT PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,

    CONSTRAINT sale_order_customer_fk
    FOREIGN KEY (customer_id)
    REFERENCES customer (customer_id)
);

CREATE TABLE IF NOT EXISTS order_item (
    order_item_id SERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL,
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

CREATE TABLE IF NOT EXISTS sale_stage (
    order_id BIGINT NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    quantity NUMERIC(12, 2) NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    order_date DATE NOT NULL,
    country VARCHAR(100) NOT NULL,
    total_price NUMERIC(14, 2) NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL
);

-- Single-table audit log. Event-specific details live in `metadata`.
CREATE TABLE IF NOT EXISTS audit.event (
    event_id UUID PRIMARY KEY,
    event_version INTEGER NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    pipeline_name VARCHAR(200) NOT NULL,
    pipeline_id VARCHAR(100) NOT NULL,
    task_name VARCHAR(250),
    task_id VARCHAR(100),
    task_attempt INTEGER,
    status VARCHAR(30) NOT NULL,
    source_system VARCHAR(100),
    source_uri TEXT,
    destination_system VARCHAR(100),
    destination_uri TEXT,
    input_row_count BIGINT,
    output_row_count BIGINT,
    rejected_row_count BIGINT,
    duplicate_row_count BIGINT,
    schema_version VARCHAR(100),
    checksum VARCHAR(200),
    duration_ms BIGINT,
    error_type VARCHAR(500),
    error_message TEXT,
    error_stacktrace TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    streaming_topic VARCHAR(250),
    streaming_partition INTEGER,
    streaming_offset BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_audit_streaming_position
    UNIQUE (streaming_topic, streaming_partition, streaming_offset)
);

CREATE INDEX idx_audit_event_pipeline_id
    ON audit.event (pipeline_id);

CREATE INDEX idx_audit_event_event_time
    ON audit.event (event_time DESC);

CREATE INDEX idx_audit_event_status
    ON audit.event (status);
