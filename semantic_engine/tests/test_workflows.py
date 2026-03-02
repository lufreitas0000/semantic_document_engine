import pytest
from semantic_engine.app_ingestion.workflows import fetch_and_store_papers

@pytest.mark.anyio
async def test_fetch_and_store_workflow_orchestrates_correctly(fake_api, fake_uow, fake_ml) -> None:
    # Notice how we just pass the injected fixtures into our workflow
    count = await fetch_and_store_papers("Quantum", fake_api, fake_uow, ml_model=fake_ml, limit=2)

    assert count == 2
    assert len(fake_uow.documents._documents) == 2
    assert fake_uow.committed is True

    saved_docs = list(fake_uow.documents._documents.values())
    assert saved_docs[0].embedding is not None
    assert len(saved_docs[0].embedding) == 384
