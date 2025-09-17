#Celery application configuration

import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("videogen", broker=redis_url, backend=redis_url)

#Test task
@celery_app.task
def test_task(message):
    return f"Task completed: {message}"
