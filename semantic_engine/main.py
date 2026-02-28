"""
Composition Root & Driving Adapter (FastAPI).
"""
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from semantic_engine.core_interfaces.uow import AbstractUnitOfWork
from semantic_engine.core_interfaces.api import AcademicGraphPort
from semantic_engine.infrastructure.database.uow import SqlAlchemyUnitOfWork
from semantic_engine.infrastructure.api.semantic_scholar import SemanticScholarClient
from semantic_engine.app_ingestion.workflows import fetch_and_store_papers

# 1. Global Infrastructure Setup
# The exact TCP coordinates and cryptography needed to reach the isolated Docker process.
DB_URL = "postgresql+psycopg2://semantic_user:super_secret_password@localhost:5432/semantic_engine_db"
# This does not connect to the database immediately. It creates a Connection Pool in RAM
engine: Engine = create_engine(url=DB_URL)
# This is a factory function (a cookie-cutter) for connections
SessionFactory: sessionmaker[Session] = sessionmaker(bind=engine)

# lifespan: FastAPI is an event-driven loop. When you hit Ctrl+C in your terminal to kill the server, you don't want to just sever the TCP sockets abruptly
# This acts as a suspension point. Everything before yield runs when the server boots. The server then pauses here and listens for HTTP requests. When you kill the server, the code after yield executes.
# engine.dispose(): Safely drains the Connection Pool, sending polite FIN packets to Postgres to close the network sockets
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    engine.dispose()

app = FastAPI(title="Semantic Document Engine", lifespan=lifespan)

# --- Dependency Providers ---
# Provider Functions. They are the only places in the application that are allowed to instantiate physical, entropy-heavy Adapters
# These functions teach FastAPI how to instantiate our adapters
def get_uow() -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory=SessionFactory)

def get_api_client() -> AcademicGraphPort:
    return SemanticScholarClient()
# ----------------------------

# 3. The Endpoints
# An ASGI router. It listens for HTTP POST requests at that URL.
@app.post(path="/ingest/")
async def ingest_papers(
    query: str,
    limit: int = 5,
    # FastAPI will automatically run get_uow() and get_api_client() and inject them
    # When a web request arrives, FastAPI pauses, executes get_uow(), takes the resulting SqlAlchemyUnitOfWork, and injects it into the uow variable.
    uow: AbstractUnitOfWork = Depends(get_uow),
    api_client: AcademicGraphPort = Depends(get_api_client)
) -> dict[str, Any]:
    """Triggers the Ingestion Workflow."""
    try:
        count: int = await fetch_and_store_papers(query=query, api_client=api_client, uow=uow, limit=limit)
        return {"message": "Success", "papers_ingested": count, "query": query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(object=e))
