#Celery application configuration

import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("videogen", broker=redis_url, backend=redis_url)

celery_app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,   #don't pile up tasks in the worker
    task_time_limit=900,            #hard kill at 15m
    task_soft_time_limit=840,       #soft timeout
)

#Test task
@celery_app.task
def test_task(message):
    return f"Task completed: {message}"

def register_tasks():
    from . import tasks

    celery_app.task(bind=True, name='api.tasks.generate_video')(tasks.generate_video)

register_tasks()


