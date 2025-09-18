#Celery application configuration

from celery import Celery
from .config import config

#Redis broker + PostgreSQL backend
celery_app = Celery("videogen", broker=config.REDIS_URL, backend=f"db+{config.DATABASE_URL}")

celery_app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,   #don't pile up tasks in the worker
    task_time_limit=config.TASK_TIME_LIMIT,            #hard kill at 15m
    task_soft_time_limit=config.TASK_SOFT_TIME_LIMIT,  #soft timeout
)

#Test task
@celery_app.task
def test_task(message):
    return f"Task completed: {message}"

def register_tasks():
    from . import tasks

    celery_app.task(
        bind=True,
        name='api.tasks.generate_video',
        autoretry_for=(Exception,), #TODO: I think this can be improved. Exception is generic.
        retry_kwargs={'max_retries': 3, 'countdown': 60},
    )(tasks.generate_video)

register_tasks()


