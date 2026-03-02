import pytest
from uuid import uuid4
from semantic_engine.core_interfaces.domain import DocumentMetadata

def test_uow_commits_on_success(fake_uow) -> None:
    doc = DocumentMetadata(id=uuid4(), title="Test", abstract="Test")
    with fake_uow:
        fake_uow.documents.add(doc)
        fake_uow.commit()

    assert fake_uow.committed is True
    assert fake_uow.rolled_back is False

def test_uow_rolls_back_on_exception(fake_uow) -> None:
    class DomainException(Exception): pass

    with pytest.raises(DomainException):
        with fake_uow:
            raise DomainException("Simulation of a system crash")

    assert fake_uow.committed is False
    assert fake_uow.rolled_back is True
