"""
Celery Application Configuration.
This acts as the orchestrator for our background ML jobs.
"""
from celery import Celery # type: ignore

# Initialize Celery and point it to our local Redis container
celery_app = Celery(
    "semantic_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    worker_prefetch_multiplier=1, # Ensure the GPU only takes 1 heavy job at a time
)
