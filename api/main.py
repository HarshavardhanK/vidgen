#main file for the api

import os
import time
from datetime import datetime

from fastapi import FastAPI, Request

import torch

from starlette.middleware.base import BaseHTTPMiddleware

from .celery_app import celery_app, test_task
from .routers import generate

from .metrics import (
    get_health_status, get_metrics_response, increment_counter,
    check_database, check_redis, get_gpu_metrics, get_active_workers, get_queue_length
)

app = FastAPI(title="videogen")

#Test Celery endpoint
@app.get("/test-celery")
def test_celery_endpoint():

    task = test_task.delay("Hello from FastAPI")
    
    return {"task_id": task.id, "status": "Task submitted"}

#Simple metrics middleware
class MetricsMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        #Record basic metrics
        increment_counter('api_requests_total')
        
        return response

app.add_middleware(MetricsMiddleware)

@app.get("/health")
async def health():
    """Health check with service status and worker metrics"""
    gpu_metrics = get_gpu_metrics()
    
    #Check all services
    db_status = await check_database()
    redis_status = await check_redis()
    
    overall_status = "healthy"
    
    if not gpu_metrics['gpu_available']:
        overall_status = "degraded"
        
    if db_status['status'] != "healthy" or redis_status['status'] != "healthy":
        overall_status = "unhealthy"
    
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

