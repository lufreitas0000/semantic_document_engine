"""
API Protocols (The Membrane).
Defines the Structural Contract for fetching academic data from external sources.
This defines the mathematical shape of *any* external academic database (Semantic Scholar, Crossref, etc.).
"""
from typing import Protocol, AsyncGenerator
from semantic_engine.core_interfaces.domain import DocumentMetadata

class AcademicGraphPort(Protocol):
    """
    Any class implementing this protocol can be injected into our Application Layer.
    """
    def fetch_papers_by_query(
        self, query: str, limit: int = 5
    ) -> AsyncGenerator[DocumentMetadata, None]:
        ...
# change name to : fetch_documents
