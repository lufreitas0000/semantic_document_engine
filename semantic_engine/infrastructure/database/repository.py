"""
SQLAlchemy implementation of the DocumentRepository Protocol.
"""
from uuid import UUID
from sqlalchemy.orm import Session
from semantic_engine.core_interfaces.domain import DocumentMetadata
from semantic_engine.infrastructure.database.models import DocumentRecord

class SqlAlchemyDocumentRepository:
    """
    Translates the mathematical Set operations (.add, .get) into SQL
    transactions via the SQLAlchemy Session.
    """
    def __init__(self, session: Session):
        self.session = session

    def add(self, document: DocumentMetadata) -> None:
        # Translate pure Domain Model -> ORM Record
        record = DocumentRecord(
            id=document.id,
            title=document.title,
            abstract=document.abstract,
            embedding=document.embedding
        )
        self.session.add(record) # Appends to the Identity Map (Session Cache)

    def get(self, document_id: UUID) -> DocumentMetadata | None:
        # Executes: SELECT * FROM documents WHERE id = ?
        record = self.session.get(DocumentRecord, document_id)
        if record is None:
            return None

        # Translate ORM Record -> pure Domain Model
        return DocumentMetadata(
            id=record.id,
            title=record.title,
            abstract=record.abstract,
            embedding=list(record.embedding) if record.embedding is not None else None
        )
