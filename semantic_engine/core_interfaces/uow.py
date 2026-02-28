"""
Unit of Work (UoW) Protocol.
Defines the atomic boundary for business transactions. It ensures that
all repository operations either commit successfully as a single unit,
or rollback entirely upon failure.
"""
from typing import Protocol
from semantic_engine.core_interfaces.repository import DocumentRepository

class AbstractUnitOfWork(Protocol):
    """
    Structural boundary for the UoW.
    It provides access to the repositories and manages the transaction lifecycle.
    """
    documents: DocumentRepository
    def __enter__(self) -> 'AbstractUnitOfWork': ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
