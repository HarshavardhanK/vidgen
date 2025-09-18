from sqlalchemy import text
from .db import get_engine
from .logging_config import logger

#This will be run during app startup to ensure the database is ready

def run_migrations():
    
    """Run database migrations on startup
    
    Note: Schema is now defined inline for K3s deployment simplicity.
    The db/init/*.sql files may no longer be needed for K3s but are kept
    for Docker Compose compatibility and reference.
    """
    
    engine = get_engine()
    
    with engine.begin() as conn:
        
        #Check if tables exist
        
        result = conn.execute(text("""
            SELECT 1 FROM information_schema.tables 
            WHERE table_name='video_generation_jobs'
        """))
        
        if not result.fetchone():
            
            logger.info("Creating database schema...")
            
            #Create tables (from db/init/01_tables.sql)
            
            conn.execute(text("""
                CREATE EXTENSION IF NOT EXISTS pgcrypto;
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
            """))
            
            #Create indexes (from db/init/03_indexes.sql)
            
            conn.execute(text("""
                CREATE INDEX idx_vgj_celery_task_id ON video_generation_jobs(celery_task_id);
                CREATE INDEX idx_vgj_user_id ON video_generation_jobs(user_id);
            """))
            
            #Create functions (from db/init/04_functions.sql)
            
            conn.execute(text("""
                CREATE OR REPLACE FUNCTION update_video_generation_result(
                    p_celery_task_id VARCHAR(155),
                    p_file_path VARCHAR(500),
                    p_file_size BIGINT,
                    p_duration REAL
                ) RETURNS BOOLEAN AS $$
                BEGIN
                    UPDATE video_generation_jobs
                    SET status = 'completed', output_file_path = p_file_path,
                        file_size_bytes = p_file_size, video_duration_seconds = p_duration,
                        completed_at = NOW(), error_message = NULL
                    WHERE celery_task_id = p_celery_task_id;
                    RETURN FOUND;
                END;
                $$ LANGUAGE plpgsql;
                
                CREATE OR REPLACE FUNCTION update_video_generation_status(
                    p_celery_task_id VARCHAR(155),
                    p_status VARCHAR(32)
                ) RETURNS BOOLEAN AS $$
                BEGIN
                    UPDATE video_generation_jobs SET status = p_status WHERE celery_task_id = p_celery_task_id;
                    RETURN FOUND;
                END;
                $$ LANGUAGE plpgsql;
                
                CREATE OR REPLACE FUNCTION update_video_generation_error(
                    p_celery_task_id VARCHAR(155),
                    p_error TEXT
                ) RETURNS BOOLEAN AS $$
                BEGIN
                    UPDATE video_generation_jobs SET status = 'failed', error_message = p_error, completed_at = NOW() WHERE celery_task_id = p_celery_task_id;
                    RETURN FOUND;
                END;
                $$ LANGUAGE plpgsql;
            """))
            
            logger.info("Database schema created successfully")
            
        else:
            logger.info("Database schema already exists")
