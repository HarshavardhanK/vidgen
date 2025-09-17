--application business logic table

DROP TABLE IF EXISTS video_generation_jobs CASCADE;

CREATE TABLE video_generation_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    celery_task_id VARCHAR(155) NOT NULL UNIQUE,

    user_id VARCHAR(100),
    prompt TEXT NOT NULL,
    duration INTEGER DEFAULT 5,
    fps INTEGER DEFAULT 8,

    priority INTEGER DEFAULT 0,
    status VARCHAR(32) DEFAULT 'pending',
    error_message TEXT,

    output_file_path VARCHAR(500),
    file_size_bytes BIGINT,
    video_duration_seconds REAL,
    
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);


