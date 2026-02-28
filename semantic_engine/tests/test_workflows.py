"""
Unit tests for the Application layer workflows using Fakes.
"""
import pytest
from typing import AsyncGenerator
from uuid import uuid4

from semantic_engine.tests.test_repository import FakeRepository
from semantic_engine.core_interfaces.domain import DocumentMetadata
from semantic_engine.tests.test_uow import FakeUnitOfWork
from semantic_engine.app_ingestion.workflows import fetch_and_store_papers

class FakeAcademicGraph:
    """An in-memory fake that yields predefined particles."""
    async def fetch_papers_by_query(
        self, query: str, limit: int = 5
    ) -> AsyncGenerator[DocumentMetadata, None]:
        yield DocumentMetadata(id=uuid4(), title=f"{query} Paper 1", abstract="Abstract 1")
        yield DocumentMetadata(id=uuid4(), title=f"{query} Paper 2", abstract="Abstract 2")

@pytest.mark.anyio
async def test_fetch_and_store_workflow_orchestrates_correctly() -> None:
    fake_api = FakeAcademicGraph()
    fake_uow = FakeUnitOfWork()

    # Execute the pure workflow
    count = await fetch_and_store_papers("Quantum", fake_api, fake_uow)

    assert count == 2

    # Type Guard: Proves to mypy that the underlying memory is our Fake
    assert isinstance(fake_uow.documents, FakeRepository)


    # Verify the documents were actually passed to the repository and committed
    assert len(fake_uow.documents._documents) == 2
    assert fake_uow.committed is True
