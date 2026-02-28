"""
Integration tests for the SQLAlchemy Adapters.
"""
import pytest
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from semantic_engine.core_interfaces.domain import DocumentMetadata
from semantic_engine.infrastructure.database.models import Base
from semantic_engine.infrastructure.database.uow import SqlAlchemyUnitOfWork

@pytest.fixture
def sqlite_session_factory():
    # The :memory: URI creates a purely volatile database in RAM
    engine = create_engine("sqlite:///:memory:")
    # Compiles our Declarative Base into CREATE TABLE strings and executes them
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

def test_sqlalchemy_uow_can_save_and_retrieve(sqlite_session_factory):
    uow = SqlAlchemyUnitOfWork(sqlite_session_factory)
    doc_id = uuid4()
    original_doc = DocumentMetadata(id=doc_id, title="Database Theory", abstract="ACID properties.")

    # Transaction 1: Write to database
    with uow:
        uow.documents.add(original_doc)
        uow.commit()

    # Transaction 2: Read from database (fresh connection)
    with uow:
        retrieved_doc = uow.documents.get(doc_id)

    assert retrieved_doc is not None
    assert retrieved_doc.id == original_doc.id
    assert retrieved_doc.title == "Database Theory"
