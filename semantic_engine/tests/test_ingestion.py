"""
Tests for the Semantic Scholar adapter using mock HTTP responses.
"""
import pytest
import httpx
from unittest.mock import AsyncMock, patch
from semantic_engine.app_ingestion.semantic_scholar import SemanticScholarClient

# pytest needs this marker to run async functions within its event loop
@pytest.mark.anyio
async def test_fetch_papers_yields_domain_models() -> None:
    client = SemanticScholarClient()

    mock_api_response = {
        "data": [
            {"title": "Attention Is All You Need", "abstract": "We propose the Transformer..."},
            {"title": "BERT", "abstract": "Language representation model..."}
        ]
    }
    # Construct a real httpx.Response object containing our fake data.
    # This avoids the "coroutine object has no attribute" error because
    # the response object natively handles .json() synchronously.
    mock_response = httpx.Response(
        status_code=200,
        json=mock_api_response,
        request=httpx.Request("GET", "https://api.semanticscholar.org/graph/v1/paper/search")
    )

    # We patch (intercept) the httpx.AsyncClient.get method at runtime.
    # Instead of hitting the network, it returns our fake JSON.
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        # When await client.get() is called, return our mock_response
        mock_get.return_value = mock_response

        # Consume the generator into a list
        results = [doc async for doc in client.fetch_papers_by_query("Transformers")]

        assert len(results) == 2
        assert results[0].title == "Attention Is All You Need"
        assert results[1].title == "BERT"
        assert results[0].abstract is not None
        # Verify the patch intercepted the call exactly once
        mock_get.assert_called_once()

