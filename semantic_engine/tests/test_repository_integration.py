import pytest
from sqlalchemy.orm import Session
from semantic_engine.infrastructure.database.repository import SqlAlchemyDocumentRepository
from semantic_engine.core_interfaces.domain import Document

def test_repository_vector_search_compiles_and_executes(postgres_container):
    """
    Verifies that the SQLAlchemy AST correctly compiles into a pgvector
    cosine distance operation (<=>) and successfully negotiates the I/O
    boundary with the Postgres container.
    """
    # 1. Arrange: Allocate local memory state
    engine = postgres_container

    # Orthogonal vectors (Cosine distance = 1.0, similarity = 0.0)
    # Parallel vectors (Cosine distance = 0.0, similarity = 1.0)
    doc_target = Document(
        id="target-uuid",
        title="Quantum Physics",
        content="Target content",
        embedding=[1.0] + [0.0] * 383  # 384-dimensional vector
    )
    doc_noise = Document(
        id="noise-uuid",
        title="Culinary Arts",
        content="Noise content",
        embedding=[0.0, 1.0] + [0.0] * 382
    )

    with Session(engine) as session:
        repo = SqlAlchemyDocumentRepository(session)

        # 2. Act: Push state to Postgres (INSERT syscalls)
        repo.add(doc_target)
        repo.add(doc_noise)
        session.commit() # Flush L1/L2 Python cache to persistent DB storage

        # Query using a vector perfectly aligned with doc_target
        query_vector = [1.0] + [0.0] * 383

        # Triggers the AST compilation -> SQL String -> TCP Network I/O
        results = repo.search_by_similarity(query_vector, limit=1)

        # 3. Assert: Verify the SIMD operations executed correctly in Postgres
        assert len(results) == 1
        assert results[0].id == "target-uuid"

        # Teardown: Clean up state for subsequent tests
        session.execute("TRUNCATE TABLE documents CASCADE;")
        session.commit()
