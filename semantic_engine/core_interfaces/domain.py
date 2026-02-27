"""
Core Domain Models.
This module defines the fundamental entities of the application.
These structures contain pure business logic and must never import
infrastructure libraries (like SQLAlchemy or FastAPI).
"""
# semantic_engine/core_interfaces/domain.py
from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class Document:
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
