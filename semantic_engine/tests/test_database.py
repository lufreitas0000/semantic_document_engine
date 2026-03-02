import pytest
import uuid
from datetime import datetime
from semantic_engine.infrastructure.database.repository import SqlAlchemyDocumentRepository
from semantic_engine.core_interfaces.domain import DocumentMetadata

def test_repository_can_save_and_retrieve_document(session_factory):
    session = session_factory()
    repo = SqlAlchemyDocumentRepository(session)

    doc_id = uuid.uuid4()
    original_doc = DocumentMetadata(
        id=doc_id,
        title="Test Container Paper",
        abstract="Running in real Postgres.",
        categories=["quant-ph"],
        authors=["Alice", "Bob"],
        published_date=datetime(2025, 1, 1),
        embedding=[0.1] * 384,
        embedding_scibert=[0.2] * 768
    )

    repo.add(original_doc)
    session.commit()

    retrieved_doc = repo.get(doc_id)

    assert retrieved_doc is not None
    assert retrieved_doc.title == "Test Container Paper"
    assert "quant-ph" in retrieved_doc.categories
    assert len(retrieved_doc.embedding_scibert) == 768
