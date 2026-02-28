"""
SQLAlchemy implementation of the DocumentRepository Protocol.
"""
from uuid import UUID
from sqlalchemy import select
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

    def search_by_embedding(self, query_embedding: list[float], limit: int = 5) -> list[DocumentMetadata]:
        # Mathematically calculate the Cosine Distance in the Postgres engine
        # We use type: ignore because mypy cannot read pgvector's C-extension methods
        # a SQL SELECT  statement. mathematical instructions for across the TCP network to the PostgreSQL daemon
        stmt = select(DocumentRecord).order_by(
            DocumentRecord.embedding.cosine_distance(query_embedding)
        ).limit(limit)

        # when Postgres replies, it sends data back as a 2D matrix.
        # scalars(): takes that grid and maps the columns back into your DocumentRecord Python object, yielding a flat list of objects.
        records = self.session.scalars(stmt).all()


        return [
            DocumentMetadata(
                id=r.id,
                title=r.title,
                abstract=r.abstract,
                embedding=list(r.embedding) if r.embedding is not None else None
            ) for r in records
        ]
