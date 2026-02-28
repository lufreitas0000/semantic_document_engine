"""
Semantic Scholar API Adapter.
Fetches academic papers via network I/O and translates the JSON payloads
into our pure Domain Models.
"""
from typing import AsyncGenerator
import httpx
from uuid import uuid4
from semantic_engine.core_interfaces.domain import DocumentMetadata

class SemanticScholarClient:
    """
    Adapter for the Semantic Scholar Graph API.
    Uses asynchronous I/O to prevent GIL locking during network latency.
    """
    def __init__(self, base_url: str = "https://api.semanticscholar.org/graph/v1"):
        self.base_url = base_url

    async def fetch_papers_by_query(
        self, query: str, limit: int = 5
    ) -> AsyncGenerator[DocumentMetadata, None]:
        """
        Executes a GET request and yields DocumentMetadata objects lazily.
        """
        url = f"{self.base_url}/paper/search"
        params: dict[str, str | int] = {
            "query": query,
            "limit": limit,
            "fields": "title,abstract"
        }

        # httpx.AsyncClient uses non-blocking OS sockets (epoll/kqueue)
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status() # Raises exception on 4xx/5xx HTTP codes

            data = response.json()

            # Generator: Yields one document at a time to prevent memory bloat
            for item in data.get("data", []):
                yield DocumentMetadata(
                    id=uuid4(), # We generate our own internal UUID for storage
                    title=item.get("title", "Unknown Title"),
                    abstract=item.get("abstract") or "No abstract available."
                )
