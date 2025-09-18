#generate router

import uuid
import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import text
from pydantic import ValidationError

from ..schemas import GenerationRequest, JobSubmissionResponse, JobStatusResponse, JobStatus, VideoInfo, VideoListResponse
from ..celery_app import celery_app
from ..config import config
from ..logging_config import logger

from ..db import get_engine
from typing import List

router = APIRouter()

@router.post("/generate", response_model=JobSubmissionResponse)
def submit_generation_job(request: GenerationRequest):
    
    #Additional validation beyond Pydantic
    if not request.user_id or not request.user_id.strip():
        raise HTTPException(
            status_code=400, 
            detail="user_id is mandatory and cannot be empty"
        )
    
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(
            status_code=400, 
            detail="prompt is mandatory and cannot be empty"
        )
    
    task = celery_app.send_task('api.tasks.generate_video', args=[request.prompt, request.fps, request.user_id])
    celery_task_id = task.id
    
    #insert DB record with the celery_task_id
    with get_engine().begin() as conn:
        
        row = conn.execute(
            text(
                """
                INSERT INTO video_generation_jobs (
                    celery_task_id, user_id, prompt, duration, fps, priority, status
                ) VALUES (
                    :task_id, :user_id, :prompt, :duration, :fps, :priority, 'pending'
                )
                RETURNING id
                """
            ),
            
            {
                "task_id": celery_task_id,
                "user_id": request.user_id,
                "prompt": request.prompt,
                "duration": 5,
                "fps": request.fps,
                "priority": 0,
            },
            
        ).one()
        
        job_id = row[0]
    
    return JobSubmissionResponse(
        success=True,
        job_id=str(job_id),
        message="Generation job submitted successfully"
    )

@router.get("/job/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, user_id: str = Query(None, description="User ID for authorization")):
    
    
    try:
        uuid.UUID(job_id)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id format")
    
    #Validate user_id if provided
    if user_id is not None and (not user_id or not user_id.strip()):
        raise HTTPException(status_code=400, detail="user_id cannot be empty if provided")
    
    #query DB + celery_taskmeta directly
    with get_engine().connect() as conn:
        
        if user_id:
            res = conn.execute(
                text(
                    """
                    SELECT ct.status, j.output_file_path, j.user_id
                    FROM video_generation_jobs j
                    LEFT JOIN celery_taskmeta ct ON j.celery_task_id = ct.task_id
                    WHERE j.id = :job_id AND j.user_id = :user_id
                    """
                ),
                {"job_id": job_id, "user_id": user_id},
            ).first()
        else:
            res = conn.execute(
                text(
                    """
                    SELECT ct.status, j.output_file_path, j.user_id
                    FROM video_generation_jobs j
                    LEFT JOIN celery_taskmeta ct ON j.celery_task_id = ct.task_id
                    WHERE j.id = :job_id
                    """
                ),
                {"job_id": job_id},
            ).first()
        
        if not res:
            
            if user_id:
                raise HTTPException(status_code=404, detail="Job not found or access denied")
            
            else:
                raise HTTPException(status_code=404, detail="Job not found")
        
        task_state, output_path = res[0], res[1]
    
    if task_state == "PENDING" or task_state is None:
        status = JobStatus.PENDING
        message = "Job is pending"
        result = None
        
    elif task_state == "STARTED":
        status = JobStatus.RUNNING
        message = "Job is running"
        result = None
        
    elif task_state == "SUCCESS":
        status = JobStatus.COMPLETED
        message = "Job completed successfully"
        result = output_path
        
    elif task_state == "FAILURE":
        status = JobStatus.FAILED
        message = "Job failed"
        result = None
        
    else:
        status = JobStatus.PENDING
        message = f"Job state: {task_state}"
        result = None
    
    return JobStatusResponse(
        job_id=job_id,
        status=status,
        message=message,
        result=result,
    )

@router.get("/videos", response_model=VideoListResponse)
async def list_completed_videos(user_id: str = Query(None, description="Filter videos by user ID")):
    
    """List all completed video generation jobs"""
    
    #Validate user_id if provided
    if user_id is not None and (not user_id or not user_id.strip()):
        raise HTTPException(status_code=400, detail="user_id cannot be empty if provided")
    
    with get_engine().connect() as conn:
        
        if user_id:
            videos_res = conn.execute(
                text(
                    """
                    SELECT id, user_id, output_file_path, file_size_bytes, submitted_at, completed_at
                    FROM video_generation_jobs 
                    WHERE status = 'completed' AND user_id = :user_id
                    ORDER BY completed_at DESC
                    """
                ),
                {"user_id": user_id}
            ).fetchall()
        else:
            videos_res = conn.execute(
                text(
                    """
                    SELECT id, user_id, output_file_path, file_size_bytes, submitted_at, completed_at
                    FROM video_generation_jobs 
                    WHERE status = 'completed'
                    ORDER BY completed_at DESC
                    """
                )
            ).fetchall()
    
    videos = []
    
    for row in videos_res:
        
        videos.append(VideoInfo(
            job_id=str(row[0]),
            user_id=row[1] or "unknown",
            filename=row[2] or "unknown",
            file_size=row[3] or 0,
            created_at=row[4],
            status=JobStatus.COMPLETED
        ))
    
    return VideoListResponse(videos=videos)

@router.get("/download/{job_id}")
async def download_video(job_id: str, user_id: str = Query(None, description="User ID for authorization")):
    """Download the video file for a completed job"""
    
    logger.info(f"Download request for job_id: {job_id}, user_id: {user_id}")
    
    try:
        uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id format")
    
    #validate user_id if provided
    if user_id is not None and (not user_id or not user_id.strip()):
        raise HTTPException(status_code=400, detail="user_id cannot be empty if provided")
    
    #query database for job info
    with get_engine().connect() as conn:
        if user_id:
            res = conn.execute(
                text(
                    """
                    SELECT user_id, status, output_file_path
                    FROM video_generation_jobs 
                    WHERE id = :job_id AND user_id = :user_id
                    """
                ),
                {"job_id": job_id, "user_id": user_id}
            ).first()
        else:
            res = conn.execute(
                text(
                    """
                    SELECT user_id, status, output_file_path
                    FROM video_generation_jobs 
                    WHERE id = :job_id
                    """
                ),
                {"job_id": job_id}
            ).first()
        
        if not res:
            logger.warning(f"Job not found or access denied: job_id={job_id}, user_id={user_id}")
            if user_id:
                raise HTTPException(status_code=404, detail="Job not found or access denied")
            else:
                raise HTTPException(status_code=404, detail="Job not found")
        
        job_user_id, job_status, output_file_path = res[0], res[1], res[2]
    
    #check if job is completed
    if job_status != 'completed':
        logger.warning(f"Job not completed: job_id={job_id}, status={job_status}")
        raise HTTPException(status_code=409, detail="Job not completed")
    
    #check if output file path exists
    if not output_file_path:
        logger.error(f"No output file path for completed job: job_id={job_id}")
        raise HTTPException(status_code=404, detail="Video file not found")
    
    #resolve full file path
    if os.path.isabs(output_file_path):
        file_path = output_file_path
        
    else:
        file_path = os.path.join(config.OUTPUT_DIR, output_file_path)
    
    #check if file exists
    if not os.path.exists(file_path):
        logger.error(f"Video file missing: {file_path}")
        raise HTTPException(status_code=404, detail="Video file not found")
    
    #get file info for logging
    file_size = os.path.getsize(file_path)
    filename = os.path.basename(file_path)
    
    logger.info(f"Serving video file: {filename}, size: {file_size} bytes")
    
    #return file response
    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )