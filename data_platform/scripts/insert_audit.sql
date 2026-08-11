INSERT INTO audit.event(
    event_id,
    event_version,
    event_type,
    event_time,
    pipeline_name,
    pipeline_id,
    task_name,
    task_id,
    task_attempt,
    status,
    metadata,
    kafka_topic,
    kafka_partition,
    kafka_offset
) VALUES (
    %(event_id) s,
    %(event_version) s,
    %(event_type) s,
    %(event_time) s,
    %(pipeline_name) s,
    %(pipeline_id) s,
    %(task_name) s,
    %(task_id) s,
    %(task_attempt) s,
    %(status) s,
    %(metadata) s,
    %(kafka_topic) s,
    %(kafka_partition) s,
    %(kafka_offset) s
)
ON CONFLICT (event_id) DO NOTHING;