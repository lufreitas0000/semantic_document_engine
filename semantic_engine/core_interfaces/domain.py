"""
Core Domain Models.
This module defines the fundamental entities of the application.
These structures contain pure business logic and must never import
infrastructure libraries (like SQLAlchemy or FastAPI).
"""
# semantic_engine/core_interfaces/domain.py
from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class DocumentMetadata:
    """
    Core domain entity representing an academic paper.

    frozen=True enforces immutability. At the CPython level, this prevents
    mutation of the instance's __dict__ after initialization.
    Immutability guarantees thread-safety (no race conditions) and
    makes the object hashable, allowing it to be stored in O(1) sets/dicts.
    """
    id: UUID
    title: str
    abstract: str

    # --- New Analytics Metadata ---
    arxiv_id: Optional[str] = None
    published_date: Optional[datetime] = None
    categories: list[str] = field(default_factory=list) # e.g., ["quant-ph", "cond-mat"]
    authors: list[str] = field(default_factory=list)    # e.g., ["John Doe", "Jane Smith"]
    author_orcids: dict[str, str | None] = field(default_factory=dict)

    # --- Dual Brain Embeddings ---
    embedding: Optional[list[float]] = None         # MiniLM (384)
    embedding_scibert: Optional[list[float]] = None # SciBERT (768)
    # The mathematical embedding of the abstract.
    # Default is None because it is computationally expensive to calculate,
