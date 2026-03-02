from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from uuid import uuid4

from semantic_engine.main import app, get_uow
from semantic_engine.core_interfaces.domain import DocumentMetadata

client = TestClient(app)

# 1. Test the Ingestion Endpoint (Mocking Celery)
@patch("semantic_engine.main.ingest_papers_task.delay")
def test_ingest_endpoint_triggers_celery(mock_delay) -> None:
    # Setup the fake Celery task return object
    mock_task = MagicMock()
    mock_task.id = "fake-uuid-1234"
    mock_delay.return_value = mock_task

    # Hit the endpoint
    response = client.post("/ingest/?query=Quantum&limit=2")

    assert response.status_code == 202
    data = response.json()
    assert data["message"] == "Ingestion job submitted successfully."
    assert data["task_id"] == "fake-uuid-1234"

    # Verify Celery was called with the exact parameters
    mock_delay.assert_called_once_with("Quantum", 2)

# 2. Test the Search Endpoint
def test_search_endpoint_success(fake_uow) -> None:
    # Seed the fake database
    doc = DocumentMetadata(
        id=uuid4(),
        title="Vector Search Paper",
        abstract="Math",
        embedding=[0.1] * 384,
        embedding_scibert=[0.2] * 768
    )
    fake_uow.documents.add(doc)

    # Override the UoW dependency
    app.dependency_overrides[get_uow] = lambda: fake_uow

    # We mock the global ml_model directly to bypass the HuggingFace engine
    with patch("semantic_engine.main.ml_model.embed_text", return_value=[0.1] * 384):
        response = client.get("/search/?query=Math&limit=5")

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "Math"
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == "Vector Search Paper"

    app.dependency_overrides.clear()
