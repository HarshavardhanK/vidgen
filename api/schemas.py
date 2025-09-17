#Define Pydantic models for the API

from pydantic import BaseModel
from typing import Optional

from enum import Enum
import uuid

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class GenerationRequest(BaseModel):
    prompt: str
    fps: int = 24
    num_videos_per_prompt: int = 1
    num_inference_steps: int = 50
    num_frames: int = 36
    guidance_scale: float = 4.5
    seed: Optional[int] = None

class JobSubmissionResponse(BaseModel):
    success: bool
    job_id: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str
    result: Optional[dict] = None