"""
Test-Driven Development (TDD) proofs for the Repository layer.
Contains in-memory Fakes designed to bypass slow Disk I/O, allowing
for instantaneous unit testing of domain logic.
"""
from semantic_engine.core_interfaces.domain import DocumentMetadata
from semantic_engine.infrastructure.database.repository import SqlAlchemyDocumentRepository

def test_fake_repository_satisfies_protocol(fake_repository, document_factory) -> None:
    # Arrange: Request a Heap allocation from the factory
    doc = document_factory(title="Quantum Gravity")

    # Act
    fake_repository.add(doc)
    retrieved_doc = fake_repository.get(doc.id)

    # Assert
    assert retrieved_doc is not None
    assert retrieved_doc.title == "Quantum Gravity"
    assert retrieved_doc == doc

def test_repository_get_all_respects_limit(db_session, document_factory) -> None:
    """
    Tests that the SqlAlchemy Adapter correctly compiles the AST limit into
    a SQL LIMIT clause, preventing out-of-memory (OOM) heap allocations.
    """
    repo = SqlAlchemyDocumentRepository(db_session)

    # Arrange: Insert 5 dummy documents using the Factory
    for i in range(5):
        doc = document_factory(title=f"Quantum Error Correction {i}")
        repo.add(doc)

    # Flush Python heap state to Postgres WAL (Write-Ahead Log)
    db_session.commit()

    # Act: Query with a strict upper bound
    results = repo.get_all(limit=3)

    # Assert: Count must exactly match the limit cardinality
    assert len(results) == 3
    assert isinstance(results[0], DocumentMetadata)
