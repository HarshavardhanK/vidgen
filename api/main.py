#main file for the api

from fastapi import FastAPI
import torch

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