--function: update results after generation

--call this function in the task script
CREATE OR REPLACE FUNCTION update_video_generation_result(
    p_celery_task_id VARCHAR(155),
    p_file_path VARCHAR(500),
    p_file_size BIGINT,
    p_duration REAL
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE video_generation_jobs 
    SET 
        status = 'completed',
        output_file_path = p_file_path,
        file_size_bytes = p_file_size,
        video_duration_seconds = p_duration,
        completed_at = NOW(),
        error_message = NULL
    WHERE celery_task_id = p_celery_task_id;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

--function: update status (processing)
CREATE OR REPLACE FUNCTION update_video_generation_status(
    p_celery_task_id VARCHAR(155),
    p_status VARCHAR(32)
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE video_generation_jobs
    SET status = p_status
    WHERE celery_task_id = p_celery_task_id;
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

--function: update error on failure
-- call this function in the task script
CREATE OR REPLACE FUNCTION update_video_generation_error(
    p_celery_task_id VARCHAR(155),
    p_error TEXT
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE video_generation_jobs
    SET status = 'failed', error_message = p_error, completed_at = NOW()
    WHERE celery_task_id = p_celery_task_id;
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;


