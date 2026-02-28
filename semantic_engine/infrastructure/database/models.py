"""
SQLAlchemy ORM Models.
These represent the physical schema of the PostgreSQL database.
Unlike our Domain Models (which hold business logic), these are strictly
data transfer objects mapped to SQL tables.
"""
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text
from uuid import UUID

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

    # Note: We will add pgvector's Vector type here in Version 1.2
