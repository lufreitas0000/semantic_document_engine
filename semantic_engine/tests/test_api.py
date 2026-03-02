from fastapi.testclient import TestClient
from uuid import uuid4
from semantic_engine.core_interfaces.domain import DocumentMetadata
from semantic_engine.main import app, get_uow, get_api_client, get_ml_model

client = TestClient(app)

def test_ingest_endpoint_success(fake_uow, fake_api, fake_ml) -> None:
    # Override FastAPI dependencies using the Pytest fixtures
    app.dependency_overrides[get_uow] = lambda: fake_uow
    app.dependency_overrides[get_api_client] = lambda: fake_api
    app.dependency_overrides[get_ml_model] = lambda: fake_ml

    response = client.post("/ingest/?query=Quantum&limit=2")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Success"
    assert data["papers_ingested"] == 2
    assert fake_uow.committed is True

    app.dependency_overrides.clear()

def test_search_endpoint_success(fake_uow, fake_ml) -> None:
    doc = DocumentMetadata(
        id=uuid4(), title="Vector Search Paper", abstract="Math", embedding=fake_ml.embed_text("Math")
    )
    fake_uow.documents.add(doc)

    app.dependency_overrides[get_uow] = lambda: fake_uow
    app.dependency_overrides[get_ml_model] = lambda: fake_ml

    response = client.get("/search/?query=Math&limit=5")

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "Math"
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == "Vector Search Paper"

    app.dependency_overrides.clear()
