"""
semantic_engine/tests/conftest.py
Global Test Fixtures and Dependency Injection.
"""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from semantic_engine.infrastructure.database.models import Base

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
