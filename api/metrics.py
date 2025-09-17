#Simple metrics tracking for video generation system
#This is a simple implementation for demo purposes. 
#Prometheus / Grafana can be used for robust monitoring

import time
from datetime import datetime
from typing import Dict, Any

#Simple in-memory counters
_metrics = {
    'api_requests_total': 0,
    'video_generations_total': 0,
    'video_generations_failed': 0,
    'start_time': time.time()
}

def increment_counter(metric_name: str, value: int = 1) -> None:
    """Increment a counter metric"""
    if metric_name in _metrics:
        _metrics[metric_name] += value

def get_counter(metric_name: str) -> int:
    """Get current counter value"""
    return _metrics.get(metric_name, 0)

def get_gpu_metrics() -> Dict[str, Any]:
    """Get GPU memory usage metrics"""
    try:
        
        import torch
        
        if torch.cuda.is_available():
            
            device = torch.cuda.current_device()
            
            return {
                'gpu_available': True,
                'gpu_memory_used_mb': torch.cuda.memory_allocated(device) // (1024**2),
                'gpu_memory_reserved_mb': torch.cuda.memory_reserved(device) // (1024**2),
                'gpu_memory_total_mb': torch.cuda.get_device_properties(device).total_memory // (1024**2)
            }
            
        else:
            return {
                'gpu_available': False,
                'gpu_memory_used_mb': 0,
                'gpu_memory_reserved_mb': 0,
                'gpu_memory_total_mb': 0
            }
            
    except Exception:
        
        return {
            'gpu_available': False,
            'gpu_memory_used_mb': 0,
            'gpu_memory_reserved_mb': 0,
            'gpu_memory_total_mb': 0
        }

def get_active_workers() -> int:
    
    """Get number of active Celery workers"""
    try:
        from .celery_app import celery_app
        
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        return len(stats) if stats else 0
    
    except Exception:
        return 0

def get_queue_length() -> int:
    
    """Get current Celery queue length"""
    try:
        from .celery_app import celery_app
        
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        if active_tasks:
            return sum(len(tasks) for tasks in active_tasks.values())
        
        return 0
    
    except Exception:
        return 0

async def check_database() -> Dict[str, Any]:
    
    """Check database connectivity"""
    try:
        
        from .db import get_engine
        from sqlalchemy import text
        
        with get_engine().begin() as conn:
            conn.execute(text("SELECT 1"))
            
        return {"status": "healthy", "error": None}
    
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_redis() -> Dict[str, Any]:
    
    """Check Redis connectivity"""
    try:
        
        from .celery_app import celery_app
        
        celery_app.control.inspect().ping()
        
        return {"status": "healthy", "error": None}
    
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

def get_health_status() -> Dict[str, Any]:
    
    """Get comprehensive health status"""
    
    gpu_metrics = get_gpu_metrics()
    
    return {
        
        'status': 'healthy' if gpu_metrics['gpu_available'] else 'degraded',
        'timestamp': datetime.utcnow().isoformat(),
        'gpu': gpu_metrics,
        'workers': {
            'active': get_active_workers(),
            'queue_length': get_queue_length()
        }
        
    }

def get_metrics_response() -> Dict[str, Any]:
    
    """Get all metrics in a simple format"""
    
    gpu_metrics = get_gpu_metrics()
    
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'system': {
            'api_requests_total': get_counter('api_requests_total'),
            'active_workers': get_active_workers(),
            'queue_length': get_queue_length()
        },
        'gpu': gpu_metrics,
        'video_generation': {
            'total': get_counter('video_generations_total'),
            'failed': get_counter('video_generations_failed')
        },
        'uptime_seconds': time.time() - _metrics.get('start_time', time.time())
    }