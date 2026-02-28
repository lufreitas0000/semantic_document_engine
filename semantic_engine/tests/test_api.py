"""
Integration Tests for the FastAPI endpoints.
"""
from fastapi.testclient import TestClient
from httpx import Response
from semantic_engine.main import app, get_uow, get_api_client
from semantic_engine.tests.test_uow import FakeUnitOfWork
from semantic_engine.tests.test_workflows import FakeAcademicGraph

# Instantiate a virtual browser to test the API locally
client = TestClient(app)

def test_ingest_endpoint_success() -> None:
    # 1. Override the physical dependencies with our RAM-based Fakes
    fake_uow = FakeUnitOfWork()
    app.dependency_overrides[get_uow] = lambda: fake_uow
    app.dependency_overrides[get_api_client] = lambda: FakeAcademicGraph()

    # 2. Simulate an HTTP POST request
    response: Response = client.post("/ingest/?query=Quantum&limit=2")

    # 3. Mathematically prove the outcome
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Success"
    assert data["papers_ingested"] == 2

    # Prove the Fake DB actually received the transaction
    assert fake_uow.committed is True

    # 4. Clean up the overrides so they don't leak into other tests
    app.dependency_overrides.clear()
