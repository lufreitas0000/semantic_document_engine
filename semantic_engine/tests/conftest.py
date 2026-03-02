"""
semantic_engine/tests/conftest.py
Global Test Fixtures and Dependency Injection.
"""
#test/conftest.py
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer # type: ignore

from typing import AsyncGenerator, Self
from uuid import UUID, uuid4
import random

from semantic_engine.infrastructure.database.models import Base
from semantic_engine.core_interfaces.domain import DocumentMetadata
from semantic_engine.core_interfaces.repository import DocumentRepository
from semantic_engine.core_interfaces.ml import TextEmbeddingPort

# --- 1. Database Testcontainer Fixtures ---

@pytest.fixture(scope="session")
def postgres_url():
    """Boots a throwaway PostgreSQL container with pgvector once per test session."""
    with PostgresContainer("pgvector/pgvector:pg16") as postgres:
        yield postgres.get_connection_url()

@pytest.fixture(scope="function")
def db_engine(postgres_url):
    """Creates a fresh database schema for every single test."""
    engine = create_engine(postgres_url)

    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture(scope="function")
def session_factory(db_engine):
    """Provides the SQLAlchemy sessionmaker bound to the test container."""
    return sessionmaker(bind=db_engine)


# --- 2. Centralized Fakes ---

class FakeRepository:
    def __init__(self) -> None:
        self._documents: dict[UUID, DocumentMetadata] = {}

    def add(self, document: DocumentMetadata) -> None:
        self._documents[document.id] = document

    def get(self, document_id: UUID) -> DocumentMetadata | None:
        return self._documents.get(document_id)

    def get_all(self, limit: int = 10) -> list[DocumentMetadata]:
        # self._documents is presumably a dict mapping UUID -> DocumentMetadata
        return list(self._documents.values())[:limit]

    def search_by_embedding(self, query_embedding: list[float], limit: int = 5) -> list[tuple[DocumentMetadata, float]]:
        docs: list[DocumentMetadata] = list(self._documents.values())[:limit]
        return [(doc, 0.0) for doc in docs]

class FakeUnitOfWork:
    def __init__(self) -> None:
        self.documents: DocumentRepository = FakeRepository()
        self.committed = False
        self.rolled_back = False
    def __enter__(self) -> Self: return self
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None: self.rollback()
    def commit(self) -> None: self.committed = True
    def rollback(self) -> None: self.rolled_back = True

class FakeAcademicGraph:
    async def fetch_papers_by_query(self, query: str, limit: int = 5) -> AsyncGenerator[DocumentMetadata, None]:
        yield DocumentMetadata(id=uuid4(), title=f"{query} Paper 1", abstract="Abstract 1")
        yield DocumentMetadata(id=uuid4(), title=f"{query} Paper 2", abstract="Abstract 2")

class FakeEmbeddingModel:
    def __init__(self, dimensions: int = 384):
        self.dimensions: int = dimensions
    def embed_text(self, text: str) -> list[float]:
        random.seed(len(text))
        return [random.uniform(-1.0, 1.0) for _ in range(self.dimensions)]

# --- 3. Fake Fixtures ---

@pytest.fixture
def fake_repository():
    return FakeRepository()

@pytest.fixture
def fake_uow():
    return FakeUnitOfWork()

@pytest.fixture
def fake_api():
    return FakeAcademicGraph()

@pytest.fixture
def fake_ml():
    return FakeEmbeddingModel()
