"""
Test-Driven Development (TDD) proofs for the Repository layer.
Contains in-memory Fakes designed to bypass slow Disk I/O, allowing
for instantaneous unit testing of domain logic.
"""
# semantic_engine/tests/test_repository.py
# we decouple our logic from slow disk I/O (Postgres) by using a "Fake". A Fake is a fully functional implementation optimized for speed (using RAM instead of Disk).
from uuid import uuid4
from semantic_engine.core_interfaces.domain import DocumentMetadata

# Pytest injects `fake_repository` directly
def test_fake_repository_satisfies_protocol(fake_repository) -> None:
    doc = DocumentMetadata(id=uuid4(), title="Quantum Gravity", abstract="A short theory.", embedding=[0.1, 0.2, 0.3])
    fake_repository.add(doc)
    retrieved_doc = fake_repository.get(doc.id)

    assert retrieved_doc is not None
    assert retrieved_doc.title == "Quantum Gravity"
    assert retrieved_doc == doc

def test_repository_get_all_respects_limit(sqlite_session): # Use your actual DB session fixture
    """
    Tests that the SqlAlchemy Adapter correctly compiles the AST limit into
    a SQL LIMIT clause, preventing out-of-memory (OOM) heap allocations.
    """
    from semantic_engine.infrastructure.database.repository import SqlAlchemyDocumentRepository
    repo = SqlAlchemyDocumentRepository(sqlite_session)

    # Arrange: Insert 5 dummy documents
    for i in range(5):
        doc = DocumentMetadata(
            id=uuid4(),
            title=f"Quantum Error Correction {i}",
            abstract="Magic state distillation...",
            arxiv_id=f"2601.0000{i}",
            published_date=None,
            categories=[],
            authors=[],
            embedding=None,
            embedding_scibert=None
        )
        repo.add(doc)

    sqlite_session.commit()

    # Act: Query with a strict upper bound
    results = repo.get_all(limit=3)

    # Assert: Count must exactly match the limit cardinality
    assert len(results) == 3
    assert isinstance(results[0], DocumentMetadata)
