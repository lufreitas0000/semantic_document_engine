import pytest
import uuid
from semantic_engine.infrastructure.database.uow import SqlAlchemyUnitOfWork
from semantic_engine.core_interfaces.domain import DocumentMetadata
from semantic_engine.infrastructure.database.models import DocumentRecord

def test_uow_commits_transaction_successfully(session_factory):
    uow = SqlAlchemyUnitOfWork(session_factory)
    doc_id = uuid.uuid4()

    doc = DocumentMetadata(
        id=doc_id, title="UOW Commit Test", abstract="Testing transactions."
    )

    with uow:
        uow.documents.add(doc)
        uow.commit()

    with session_factory() as session:
        record = session.query(DocumentRecord).filter_by(id=doc_id).first()
        assert record is not None
        assert record.title == "UOW Commit Test"

def test_uow_rolls_back_on_exception(session_factory):
    uow = SqlAlchemyUnitOfWork(session_factory)
    doc_id = uuid.uuid4()

    doc = DocumentMetadata(
        id=doc_id, title="UOW Rollback Test", abstract="Testing rollbacks."
    )

    try:
        with uow:
            uow.documents.add(doc)
            raise RuntimeError("Simulated Crash")
    except RuntimeError:
        pass

    with session_factory() as session:
        record = session.query(DocumentRecord).filter_by(id=doc_id).first()
        assert record is None
