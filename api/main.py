#main file for the api

import os
import time
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import torch

from starlette.middleware.base import BaseHTTPMiddleware

from .celery_app import celery_app, test_task
from .routers import generate
from .logging_config import logger
from .config import config

from .metrics import (
    get_health_status, get_metrics_response, increment_counter,
    check_database, check_redis, get_gpu_metrics, get_active_workers, get_queue_length
)

#Initialize logging
logger.info("FastAPI application starting up")

#Log configuration
logger.info(f"Configuration loaded - Environment: {config.ENVIRONMENT}, Debug: {config.DEBUG}")

app = FastAPI(title="videogen")

#Custom validation error handler for standardized responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for validation errors to provide clean, standardized responses
    """
    errors = []
    
    for error in exc.errors():
        
        field_name = ".".join(str(loc) for loc in error["loc"][1:])
        
        error_msg = error["msg"]
        error_type = error["type"]
        
        #Create user-friendly error messages
        if error_type == "missing":
            
            if field_name == "user_id":
                message = "user_id is required and cannot be empty"
                
            elif field_name == "prompt":
                message = "prompt is required and cannot be empty"
            else:
                message = f"{field_name} is required"
                
        elif error_type == "value_error":
            message = error_msg
            
        elif "greater_than_equal" in error_type or "less_than_equal" in error_type:
            message = f"{field_name} value is out of valid range"
            
        else:
            message = f"{field_name}: {error_msg}"
        
        errors.append({
            "field": field_name,
            "message": message,
            "type": error_type
        })
    
    return JSONResponse(
        status_code=422, #unprocessable entity
        content={
            "success": False,
            "error": "Validation failed",
            "details": errors,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

#Custom HTTP exception handler for consistent error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for HTTP exceptions to provide consistent error format
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.on_event("startup")
async def startup_event():
    from .db_init import run_migrations
    run_migrations()
    logger.info("Video generation API started successfully")

#Test Celery endpoint
@app.get("/test-celery")
def test_celery_endpoint():

    task = test_task.delay("Hello from FastAPI")
    
    return {"task_id": task.id, "status": "Task submitted"}

#Simple metrics middleware
class MetricsMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        logger.info(f"Request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        #Record basic metrics
        increment_counter('api_requests_total')
        
        duration = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {duration:.3f}s")
        
        return response

app.add_middleware(MetricsMiddleware)

@app.get("/health")
async def health():
    
    """Health check with service status and worker metrics"""
    
    logger.info("Health check requested")
    gpu_metrics = get_gpu_metrics()
    
    #Check all services
    db_status = await check_database()
    redis_status = await check_redis()
    
    overall_status = "healthy"
        
    if db_status['status'] != "healthy" or redis_status['status'] != "healthy":
        overall_status = "unhealthy"
    
    logger.info(f"Health check result: {overall_status}")
    
    return {
        
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "gpu": gpu_metrics,
        
        "services": {
            "database": db_status,
            "redis": redis_status,
            "celery_workers": get_active_workers()
        },
        
        "workers": {
            "active": get_active_workers(),
            "queue_length": get_queue_length()
        }
    }


@app.get("/task-result/{task_id}")
def get_task_result(task_id: str):
    
    task = test_task.AsyncResult(task_id)
    
    if task.state == "PENDING":
        return {"state": task.state, "result": None}
    
    elif task.state == "SUCCESS":
        return {"state": task.state, "result": task.result}
    
    else:
        return {"state": task.state, "result": str(task.info)}

@app.get("/metrics")
def metrics():
    """Basic metrics endpoint with key performance indicators"""
    return get_metrics_response()

#include routers
app.include_router(generate.router, prefix="/api/v1", tags=["generation"])

