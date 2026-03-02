import pytest
from sqlalchemy import text
from semantic_engine.infrastructure.database.repository import SqlAlchemyDocumentRepository

def test_repository_vector_search_routing(db_session, document_factory):
    """
    Verifies dynamic AST routing for SIMD vector operations.
    Ensures both 384d (MiniLM) and 768d (SciBERT) branches compile
    and execute successfully over the Postgres TCP boundary.
    """
    # 1. Arrange: Allocate Repository and Entities on the Heap
    repo = SqlAlchemyDocumentRepository(db_session)

    doc_target = document_factory(
        title="Target Matrix",
        embedding=[1.0] + [0.0] * 383,           # 384d
        embedding_scibert=[1.0] + [0.0] * 767    # 768d
    )
    doc_noise = document_factory(
        title="Orthogonal Noise",
        embedding=[0.0, 1.0] + [0.0] * 382,
        embedding_scibert=[0.0, 1.0] + [0.0] * 766
    )

    # 2. Act: Push state to persistent storage (Syscalls)
    repo.add(doc_target)
    repo.add(doc_noise)
    db_session.commit()

    # 3. Assert: 384-dimensional branch execution (MiniLM)
    results_384 = repo.search_by_embedding([1.0] + [0.0] * 383, limit=1)
    assert len(results_384) == 1
    assert results_384[0][0].id == doc_target.id
    assert results_384[0][1] < 1e-5

    # 4. Assert: 768-dimensional branch execution (SciBERT)
    results_768 = repo.search_by_embedding([1.0] + [0.0] * 767, limit=1)
    assert len(results_768) == 1
    assert results_768[0][0].id == doc_target.id
    assert results_768[0][1] < 1e-5

    # 5. Teardown: Clean up state
    db_session.execute(text("TRUNCATE TABLE documents CASCADE;"))
    db_session.commit()
