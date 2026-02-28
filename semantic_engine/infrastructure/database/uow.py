"""
SQLAlchemy implementation of the Unit of Work Protocol.
Manages the TCP socket connection and transaction boundaries.
"""
from sqlalchemy.orm import sessionmaker
from typing import Self
from semantic_engine.core_interfaces.repository import DocumentRepository
from semantic_engine.infrastructure.database.repository import SqlAlchemyDocumentRepository

class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    def __enter__(self) -> Self:
        # Allocates a database connection from the pool and starts a transaction
        self.session = self.session_factory()
        self.documents: DocumentRepository = SqlAlchemyDocumentRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()
        # Returns the TCP socket back to the connection pool
        self.session.close()

    def commit(self) -> None:
        # Flushes the AST to the PostgreSQL WAL
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
