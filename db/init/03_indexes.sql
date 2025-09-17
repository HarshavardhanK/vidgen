
CREATE INDEX IF NOT EXISTS idx_vgj_celery_task_id ON video_generation_jobs(celery_task_id);
CREATE INDEX IF NOT EXISTS idx_vgj_user_id ON video_generation_jobs(user_id);


