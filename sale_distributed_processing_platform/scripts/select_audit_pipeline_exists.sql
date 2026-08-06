SELECT EXISTS (
    SELECT 1
    FROM audit.pipeline
    WHERE pipeline_id = :pipeline_id
);
