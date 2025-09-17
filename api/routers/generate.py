#generate router

import uuid
from fastapi import APIRouter, HTTPException
from ..schemas import GenerationRequest, JobSubmissionResponse, JobStatusResponse, JobStatus

router = APIRouter()

#simple dummy storage for testing
dummy_jobs = {}

def create_dummy_job(request: GenerationRequest) -> str:
    job_id = str(uuid.uuid4())
    dummy_jobs[job_id] = {
        "id": job_id,
        "status": JobStatus.PENDING,
        "request": request,
        "result": None,
        "error": None
    }
    return job_id

def get_dummy_job(job_id: str):
    return dummy_jobs.get(job_id)

@router.post("/generate", response_model=JobSubmissionResponse)
async def generate_video(request: GenerationRequest):
    try:
        job_id = create_dummy_job(request)
        
        return JobSubmissionResponse(
            success=True,
            job_id=job_id,
            message="Video generation job submitted successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit job: {str(e)}")

@router.get("/job/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    job = get_dummy_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    message = "Job is pending"
    
    if job["status"] == JobStatus.RUNNING:
        message = "Job is running"
        
    elif job["status"] == JobStatus.COMPLETED:
        message = "Job completed successfully"
        
    elif job["status"] == JobStatus.FAILED:
        message = f"Job failed: {job.get('error', 'Unknown error')}"
    
    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        message=message,
        result=job.get("result")
    )