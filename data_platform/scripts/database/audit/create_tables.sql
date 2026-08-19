CREATE SCHEMA IF NOT EXISTS audit;

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
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_event_pipeline_id
    ON audit.event (pipeline_id);

CREATE INDEX IF NOT EXISTS idx_audit_event_event_time
    ON audit.event (event_time DESC);

CREATE INDEX IF NOT EXISTS idx_audit_event_status
    ON audit.event (status);
