"""
Test-Driven Development (TDD) proofs for the Repository layer.
Contains in-memory Fakes designed to bypass slow Disk I/O, allowing
for instantaneous unit testing of domain logic.
"""
# semantic_engine/tests/test_repository.py
# we decouple our logic from slow disk I/O (Postgres) by using a "Fake". A Fake is a fully functional implementation optimized for speed (using RAM instead of Disk).

import pytest
from uuid import uuid4, UUID
from semantic_engine.core_interfaces.domain import Document
from semantic_engine.core_interfaces.repository import DocumentRepository

class FakeRepository:
    """
    An in-memory implementation of DocumentRepository.
    Uses a Python dict (a C-level Hash Map) for O(1) lookups.
    """
    def __init__(self) -> None:
        self._documents: dict[UUID, Document] = {}

    def add(self, document: Document) -> None:
        self._documents[document.id] = document

    def get(self, document_id: UUID) -> Document | None:
        return self._documents.get(document_id)

def test_fake_repository_satisfies_protocol() -> None:
    """
    Static analysis check: If FakeRepository does not match the Protocol,
    mypy will fail before this test ever runs.
    """
    repo: DocumentRepository = FakeRepository()
    doc = Document(id=uuid4(), title="Quantum Gravity", abstract="A short theory.")

    repo.add(doc)
    retrieved_doc = repo.get(doc.id)

    assert retrieved_doc is not None
    assert retrieved_doc.title == "Quantum Gravity"
    # Testing hashability/equality. Dataclasses auto-generate __eq__
    assert retrieved_doc == doc
