import pytest
import uuid
from semantic_engine.infrastructure.database.uow import SqlAlchemyUnitOfWork
from semantic_engine.core_interfaces.domain import DocumentMetadata

def test_uow_commits_transaction_successfully(session_factory):
    uow = SqlAlchemyUnitOfWork(session_factory)
    doc_id = uuid.uuid4()

    doc = DocumentMetadata(
        id=doc_id,
        title="UOW Commit Test",
        abstract="Testing transactions.",
        categories=[],
        authors=[]
    )

    with uow:
        uow.documents.save(doc)
        uow.commit()

    # Verify outside the transaction boundary
    session = session_factory()
    from semantic_engine.infrastructure.database.models import DocumentRecord
    record = session.query(DocumentRecord).filter_by(id=doc_id).first()

    assert record is not None
    assert record.title == "UOW Commit Test"

def test_uow_rolls_back_on_exception(session_factory):
    uow = SqlAlchemyUnitOfWork(session_factory)
    doc_id = uuid.uuid4()

    doc = DocumentMetadata(
        id=doc_id,
        title="UOW Rollback Test",
        abstract="Testing rollbacks.",
        categories=[],
        authors=[]
    )

    try:
        with uow:
            uow.documents.save(doc)
            raise RuntimeError("Simulated Crash")
    except RuntimeError:
        pass

    session = session_factory()
    from semantic_engine.infrastructure.database.models import DocumentRecord
    record = session.query(DocumentRecord).filter_by(id=doc_id).first()

    # Prove the database successfully rolled back the save
    assert record is None
