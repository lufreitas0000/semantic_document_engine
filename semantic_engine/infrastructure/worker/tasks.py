"""
Celery Task Definitions.
These functions run entirely in the background, freeing up the Web Server.
"""
import os
from dotenv import load_dotenv
load_dotenv()

import asyncio
from uuid import uuid4

from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from semantic_engine.infrastructure.worker.celery_app import celery_app
from semantic_engine.app_ingestion.workflows import fetch_and_store_papers

# --- Isolate Heavy Imports ---
from semantic_engine.infrastructure.api.arxiv import ArxivClient
from semantic_engine.infrastructure.database.uow import SqlAlchemyUnitOfWork
from semantic_engine.infrastructure.ml.sentence_transformer import HuggingFaceEmbeddingModel

# 1. Provide the Worker with its own isolated Database Connection
# This breaks the circular import with main.py
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is missing!")
worker_engine = create_engine(DATABASE_URL)
WorkerSessionFactory = sessionmaker(bind=worker_engine)

# 2. Initialize the real adapters for the worker process
api_client = ArxivClient()
ml_model = HuggingFaceEmbeddingModel(model_name="allenai/scibert_scivocab_uncased")

def get_worker_uow() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(WorkerSessionFactory)

@celery_app.task(bind=True, name="ingest_papers_task")
def ingest_papers_task(self, query: str, limit: int):
    """
    A Celery Task that wraps our asynchronous core workflow.
    """
    self.update_state(state='PROGRESS', meta={'status': 'Fetching and Embedding...'})

    uow = get_worker_uow()

    count = asyncio.run(
        fetch_and_store_papers(
            query=query,
            api_port=api_client,
            uow=uow,
            ml_model=ml_model,
            limit=limit
        )
    )

    return {"status": "COMPLETED", "papers_ingested": count}
