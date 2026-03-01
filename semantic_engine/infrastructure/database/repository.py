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

    def search_by_embedding(self, query_embedding: list[float], limit: int = 5) -> list[tuple[DocumentMetadata, float]]:
        # 1. Ask Postgres to label the distance calculation as a column
        distance_col = DocumentRecord.embedding.cosine_distance(query_embedding).label("distance") # type: ignore

        # Mathematically calculate the Cosine Distance in the Postgres engine
        # We use type: ignore because mypy cannot read pgvector's C-extension methods
        # a SQL SELECT  statement. mathematical instructions for across the TCP network to the PostgreSQL daemon

        # 2. Select both the Record AND the Distance
        stmt = (
            select(DocumentRecord, distance_col)
            .where(DocumentRecord.embedding.is_not(None))
            .order_by(distance_col)
            .limit(limit)
        )
        # 3. execute() returns raw rows instead of just objects
        rows = self.session.execute(stmt).all()

        # 4. Map row[0] (The Record) and row[1] (The Float Distance)
        return [
            (
                DocumentMetadata(
                    id=row[0].id,
                    title=row[0].title,
                    abstract=row[0].abstract,
                    embedding=list(row[0].embedding) if row[0].embedding is not None else None
                ),
                float(row[1])
            ) for row in rows
        ]
