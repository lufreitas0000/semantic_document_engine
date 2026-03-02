"""
Infrastructure Protocols.
This module defines the Structural Subtyping boundaries (Interfaces)
for side-effectful operations (I/O, Disk, Network). It dictates *what* must be done without defining *how* it is done.
"""
# semantic_engine/core_interfaces/repository.py
from typing import Protocol, Optional
from uuid import UUID
from semantic_engine.core_interfaces.domain import DocumentMetadata

class DocumentRepository(Protocol):
    """
    Structural Subtyping boundary (Duck Typing validated at compile-time).
    Any class with these exact method signatures is mathematically a
    DocumentRepository. No nominal inheritance (e.g., subclassing ABC) is required,
    avoiding deep Method Resolution Order (MRO) tree traversals.
    """
    def add(self, document: DocumentMetadata) -> None:
        ...

    def get(self, document_id: UUID) -> Optional[DocumentMetadata]:
        ...

    def get_all(self, limit: int = 10) -> list[DocumentMetadata]:
        ...

    def search_by_embedding(self, query_embedding: list[float], limit: int = 5) -> list[tuple[DocumentMetadata, float]]:
        ...

