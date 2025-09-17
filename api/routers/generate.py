#generate router

import uuid
from fastapi import APIRouter, HTTPException
from ..schemas import GenerationRequest, JobSubmissionResponse, JobStatusResponse, JobStatus
from ..celery_app import celery_app

router = APIRouter()

@router.post("/generate", response_model=JobSubmissionResponse)
def submit_generation_job(request: GenerationRequest):
    
    #Submit task to Celery
    task = celery_app.send_task('api.tasks.generate_video', args=[request.prompt, request.fps])
    
    return JobSubmissionResponse(
        success=True,
        job_id=task.id,
        message="Generation job submitted successfully"
    )

@router.get("/job/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    
    #get task from Celery
    task = celery_app.AsyncResult(job_id)
    
    if task.state == "PENDING":
        status = JobStatus.PENDING
        message = "Job is pending"
        result = None
        
    elif task.state == "STARTED":
        status = JobStatus.RUNNING
        message = "Job is running"
        result = None
        
    elif task.state == "SUCCESS":
        status = JobStatus.COMPLETED
        message = "Job completed successfully"
        result = task.result
        
    elif task.state == "FAILURE":
        status = JobStatus.FAILED
        message = f"Job failed: {str(task.info)}"
        result = None
        
    else:
        status = JobStatus.PENDING
        message = f"Job state: {task.state}"
        result = None
    
    return JobStatusResponse(
        job_id=job_id,
        status=status,
        message=message,
        result=result
    )