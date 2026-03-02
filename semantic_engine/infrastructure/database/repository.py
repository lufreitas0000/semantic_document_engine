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
        record = self._to_model(document)
        self.session.add(record)

    def get(self, document_id: UUID) -> DocumentMetadata | None:
        record = self.session.query(DocumentRecord).filter_by(id=document_id).first()
        if record:
            return self._to_domain(record)
        return None


    def search_by_embedding(self, query_embedding: list[float], limit: int = 5) -> list[tuple[DocumentMetadata, float]]:
        # 1. Dynamic Hardware Routing based on Vector Dimensionality
        vector_length = len(query_embedding)

        if vector_length == 384:
            # Route to the MiniLM column
            vector_column = DocumentRecord.embedding
        elif vector_length == 768:
            # Route to the SciBERT column
            vector_column = DocumentRecord.embedding_scibert
        else:
            raise ValueError(f"Unsupported embedding dimension: {vector_length}. Expected 384 (MiniLM) or 768 (SciBERT).")

        # 2. Ask Postgres to mathematically calculate the Cosine Distance
        distance_col = vector_column.cosine_distance(query_embedding).label("distance") # type: ignore

        # 3. Modern SQLAlchemy 2.0 Query Construction
        stmt = (
            select(DocumentRecord, distance_col)
            .where(vector_column.is_not(None))
            .order_by(distance_col)
            .limit(limit)
        )

        # 4. Execute across the network to the Postgres daemon
        rows = self.session.execute(stmt).all()

        # 5. Map the results using our centralized Hexagonal adapter
        return [
            (self._to_domain(row[0]), float(row[1])) for row in rows
        ]

    def _to_model(self, doc: DocumentMetadata) -> DocumentRecord:
        return DocumentRecord(
            id=doc.id,
            title=doc.title,
            abstract=doc.abstract,
            arxiv_id=doc.arxiv_id,
            published_date=doc.published_date,
            categories=doc.categories,
            authors=doc.authors,
            embedding=doc.embedding,
            embedding_scibert=doc.embedding_scibert
        )

    def _to_domain(self, record: DocumentRecord) -> DocumentMetadata:
        return DocumentMetadata(
            id=record.id,
            title=record.title,
            abstract=record.abstract,
            arxiv_id=record.arxiv_id,
            published_date=record.published_date,
            categories=record.categories or [],
            authors=record.authors or [],
            embedding=record.embedding,
            embedding_scibert=record.embedding_scibert
        )



