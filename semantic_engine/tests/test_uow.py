"""
TDD proofs for the Unit of Work pattern.
Ensures that the context manager correctly evaluates commit and rollback paths.
"""
import pytest
from uuid import uuid4
from semantic_engine.core_interfaces.domain import DocumentMetadata
from semantic_engine.tests.test_repository import FakeRepository

class FakeUnitOfWork:
    """    In-memory simulation of a database transaction.    """
    def __init__(self) -> None:
        self.documents = FakeRepository()
        self.committed = False
        self.rolled_back = False
    def __enter__(self) -> 'FakeUnitOfWork':
        return self
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()
    def commit(self) -> None:
        self.committed = True
    def rollback(self) -> None:
        self.rolled_back = True


def test_uow_commits_on_success() -> None:
    uow = FakeUnitOfWork()
    doc = DocumentMetadata(id=uuid4(), title="Test", abstract="Test")

    with uow:
        uow.documents.add(doc)
        uow.commit()

    assert uow.committed is True
    assert uow.rolled_back is False

def test_uow_rolls_back_on_exception() -> None:
    uow = FakeUnitOfWork()

    class DomainException(Exception):
        pass

    with pytest.raises(DomainException):
        with uow:
            raise DomainException("Simulation of a system crash")

    assert uow.committed is False
    assert uow.rolled_back is True
