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
    streaming_topic,
    streaming_partition,
    streaming_offset
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
    %(streaming_topic) s,
    %(streaming_partition) s,
    %(streaming_offset) s
)
ON CONFLICT (event_id) DO NOTHING;