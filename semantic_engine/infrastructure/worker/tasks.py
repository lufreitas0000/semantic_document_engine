"""
Celery Task Definitions.
These functions run entirely in the background, freeing up the Web Server.
"""
import asyncio
from uuid import uuid4

from semantic_engine.infrastructure.worker.celery_app import celery_app
from semantic_engine.app_ingestion.workflows import fetch_and_store_papers

# --- Isolate Heavy Imports ---
# We instantiate these globally in the worker process so they stay cached in VRAM
from semantic_engine.infrastructure.api.arxiv import ArxivClient
from semantic_engine.infrastructure.database.uow import SqlAlchemyUnitOfWork
from semantic_engine.infrastructure.ml.sentence_transformer import HuggingFaceEmbeddingModel
from semantic_engine.main import SessionFactory

# Initialize the real adapters for the worker process
api_client = ArxivClient()
ml_model = HuggingFaceEmbeddingModel(model_name="allenai/scibert_scivocab_uncased")

def get_worker_uow() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(SessionFactory)

@celery_app.task(bind=True, name="ingest_papers_task")
def ingest_papers_task(self, query: str, limit: int):
    """
    A Celery Task that wraps our asynchronous core workflow.
    Because Celery is synchronous, we use asyncio.run() to execute the workflow.
    """
    # 1. Update status to inform the Web Server we have started
    self.update_state(state='PROGRESS', meta={'status': 'Fetching and Embedding...'})

    # 2. Run the async Hexagonal workflow
    uow = get_worker_uow()

    # Run the coroutine in the synchronous Celery worker
    count = asyncio.run(
        fetch_and_store_papers(
            query=query,
            api_port=api_client,
            uow=uow,
            ml_model=ml_model,
            limit=limit
        )
    )

    # 3. Return the final success metric
    return {"status": "COMPLETED", "papers_ingested": count}
