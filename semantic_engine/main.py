"""
Composition Root & Driving Adapter (FastAPI).
This is where all the isolated Hexagonal layers are finally wired together.
It receives HTTP requests,
instantiates the Infrastructure adapters,
and triggers the pure Application workflows.
"""
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI, HTTPException
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from semantic_engine.infrastructure.database.uow import SqlAlchemyUnitOfWork
from semantic_engine.infrastructure.api.semantic_scholar import SemanticScholarClient
from semantic_engine.app_ingestion.workflows import fetch_and_store_papers

# 1. Global Infrastructure Setup
# In production, this URL would come from os.getenv()
DB_URL = "postgresql+psycopg2://semantic_user:super_secret_password@localhost:5432/semantic_engine_db"
engine: Engine = create_engine(url=DB_URL)
SessionFactory: sessionmaker[Session] = sessionmaker(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: We could verify DB connections here
    yield
    # Shutdown: Clean up connection pools
    engine.dispose()

# 2. Instantiate the API
app = FastAPI(
    title="Semantic Document Engine",
    description="Hexagonal Architecture API for Academic Papers",
    lifespan=lifespan
)

# 3. The Endpoints
@app.post(path="/ingest/")
async def ingest_papers(query: str, limit: int = 5) -> dict[str, Any]:
    """
    Triggers the Ingestion Workflow.
    """
    # Instantiate the Adapters (Dependency Injection)
    uow = SqlAlchemyUnitOfWork(session_factory=SessionFactory)
    api_client = SemanticScholarClient()

    try:
        # Trigger the pure workflow
        count: int = await fetch_and_store_papers(query=query, api_client=api_client, uow=uow, limit=limit)
        return {"message": "Success", "papers_ingested": count, "query": query}
    except Exception as e:
        # Catch any unexpected entropy and return a 500
        raise HTTPException(status_code=500, detail=str(object=e))
