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
