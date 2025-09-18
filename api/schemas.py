#Define Pydantic models for the API

from pydantic import BaseModel, Field, validator
from typing import Optional, Union, List
from datetime import datetime

from enum import Enum
import uuid

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class GenerationRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="User ID is required and cannot be empty")
    prompt: str = Field(..., min_length=1, description="Prompt is required and cannot be empty")
    fps: int = Field(24, ge=1, le=60, description="FPS must be between 1 and 60")
    
    num_videos_per_prompt: int = Field(1, ge=1, le=10, description="Number of videos must be between 1 and 10")
    num_inference_steps: int = Field(50, ge=1, le=200, description="Inference steps must be between 1 and 200")
    num_frames: int = Field(36, ge=1, le=200, description="Number of frames must be between 1 and 200")
    
    guidance_scale: float = Field(4.5, ge=0.1, le=20.0, description="Guidance scale must be between 0.1 and 20.0")
    seed: Optional[int] = Field(None, ge=0, description="Seed must be non-negative if provided")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError('user_id is required and cannot be empty or whitespace')
        return v.strip()
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError('prompt is required and cannot be empty or whitespace')
        return v.strip()

class JobSubmissionResponse(BaseModel):
    success: bool
    job_id: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str
    result: Optional[Union[str, dict]] = None

class VideoInfo(BaseModel):
    job_id: str
    user_id: str
    filename: str
    file_size: int
    created_at: datetime
    status: JobStatus

class VideoListResponse(BaseModel):
    videos: List[VideoInfo]