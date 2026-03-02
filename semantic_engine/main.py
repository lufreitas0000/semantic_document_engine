"""
FastAPI Web Application.
This is the primary entry point for HTTP traffic. It acts as a lightweight router,
pushing heavy machine learning tasks to the Celery Message Broker.
"""
import os
from dotenv import load_dotenv

# Load environment variables before initializing any Heavy ML models
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from typing import List, Dict, Any
from pydantic import BaseModel
from contextlib import asynccontextmanager
from celery.result import AsyncResult # type: ignore

from semantic_engine.infrastructure.database.uow import SqlAlchemyUnitOfWork
from semantic_engine.infrastructure.ml.sentence_transformer import HuggingFaceEmbeddingModel
from semantic_engine.infrastructure.database.models import Base
from semantic_engine.infrastructure.worker.tasks import ingest_papers_task
from semantic_engine.infrastructure.worker.celery_app import celery_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- Database & ML Initialization ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is missing!")
engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine)

# Note: We still load the ML model in the Web API because the /search endpoint
# needs to embed the 5-word user query instantly. (This is very fast).
ml_model = HuggingFaceEmbeddingModel(model_name="allenai/scibert_scivocab_uncased")

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield

app = FastAPI(title="Semantic Document Engine", lifespan=lifespan)

def get_uow():
    return SqlAlchemyUnitOfWork(SessionFactory)

# --- Schemas ---
class SearchResult(BaseModel):
    title: str
    abstract: str
    distance: float

# --- Endpoints ---

@app.post("/ingest/", status_code=status.HTTP_202_ACCEPTED)
async def ingest_papers(query: str, limit: int = 5):
    """
    Submits a bulk download and ML embedding job to the background worker.
    Returns immediately so the web server does not freeze.
    """
    # .delay() pushes the exact function arguments into the Redis Queue
    task = ingest_papers_task.delay(query, limit)

    return {
        "message": "Ingestion job submitted successfully.",
        "task_id": task.id,
        "status_url": f"/tasks/{task.id}"
    }

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Allows the client (Streamlit) to poll the status of a specific background job.
    """
    task_result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task_result.status,
    }

    if task_result.state == 'SUCCESS':
        response["result"] = task_result.result
    elif task_result.state == 'FAILURE':
        response["error"] = str(task_result.info)

    return response

@app.get("/search/", response_model=dict)
async def search_papers(query: str, limit: int = 5, uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    """
    Performs a real-time semantic search using Postgres pgvector.
    """
    query_vector = ml_model.embed_text(query)

    with uow:
        results = uow.documents.search_by_embedding(query_vector, limit)

    formatted_results = [
        SearchResult(title=doc.title, abstract=doc.abstract, distance=dist)
        for doc, dist in results
    ]

    return {"query": query, "results": formatted_results}


@app.get("/documents/", response_model=List[Dict[str, Any]])
def get_ingested_documents(
    limit: int = 10,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
):
    """
    Retrieves ingested documents from the database.
    Proves that the Celery worker successfully committed the transaction.
    """
    with uow:
        # Calls our new O(1) query method
        documents = uow.documents.get_all(limit=limit)

        # Map Domain Entities to DTOs
        return [
            {
                "id": str(doc.id),
                "title": doc.title,
                "arxiv_id": doc.arxiv_id,
                # True if either vector space mapping exists
                "is_embedded": doc.embedding is not None or doc.embedding_scibert is not None
            }
            for doc in documents
        ]
