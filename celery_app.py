# /home/jdennis/Projects/JennAI/src/core/celery_app.py
from celery import Celery
import os

# The broker URL tells Celery where to send and receive messages.
# We'll pull it from an environment variable for flexibility, defaulting to a local Redis instance.
# Example: REDIS_URL=redis://localhost:6379/0
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    'vividai_tasks',
    broker=redis_url,
    backend=redis_url,
    include=['ml_tasks'] # Auto-discover tasks from ml_tasks.py at the root
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)