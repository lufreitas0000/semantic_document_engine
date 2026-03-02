"""
SQLAlchemy ORM Models.
These represent the physical schema of the PostgreSQL database.
Unlike our Domain Models (which hold business logic), these are strictly
data transfer objects mapped to SQL tables.
"""
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.dialects.postgresql import ARRAY
from uuid import UUID
from datetime import datetime
from pgvector.sqlalchemy import Vector  # type: ignore

class Base(DeclarativeBase):
    """
    The Declarative Base creates a registry. Any class inheriting from this
    is automatically tracked by SQLAlchemy's metaclass machinery to generate
    SQL CREATE TABLE statements.
    """
    pass

class DocumentRecord(Base):
    __tablename__ = "documents"

    # Mapped[...] enforces strict static typing for mypy, while mapped_column
    # provides the runtime SQL configuration.
    id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    abstract: Mapped[str] = mapped_column(Text)
    # --- New Analytics Metadata ---
    arxiv_id: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    published_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    categories: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    authors: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)

    # --- Dual Brain Embeddings ---
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=True)
    embedding_scibert: Mapped[list[float]] = mapped_column(Vector(768), nullable=True)
