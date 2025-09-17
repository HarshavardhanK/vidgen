#main file for the api

from fastapi import FastAPI
import torch
import os
from .celery_app import celery_app, test_task
from .routers import generate

app = FastAPI(title="videogen")

@app.get("/health")
def health():
    
    ok = torch.cuda.is_available()
    gpu = {}
    
    if ok:
        
        i = torch.cuda.current_device()
        
        gpu = {
            "name": torch.cuda.get_device_name(i),
            "total_mb": torch.cuda.get_device_properties(i).total_memory // (1024**2),
            "mem_allocated_mb": torch.cuda.memory_allocated(i) // (1024**2),
            "mem_reserved_mb": torch.cuda.memory_reserved(i) // (1024**2),
        }
        
    return {"ok": ok, "gpu": gpu}

@app.get("/test-celery")
def test_celery_endpoint():

    task = test_task.delay("Hello from FastAPI")
    
    return {"task_id": task.id, "status": "Task submitted"}

@app.get("/task-result/{task_id}")
def get_task_result(task_id: str):
    
    task = test_task.AsyncResult(task_id)
    
    if task.state == "PENDING":
        return {"state": task.state, "result": None}
    
    elif task.state == "SUCCESS":
        return {"state": task.state, "result": task.result}
    
    else:
        return {"state": task.state, "result": str(task.info)}

#include routers
app.include_router(generate.router, prefix="/api/v1", tags=["generation"])

