"""
arXiv API Adapter.
Implements the AcademicGraphPort Protocol.
"""
import httpx
import xml.etree.ElementTree as ET
from uuid import uuid4
from typing import AsyncGenerator

from semantic_engine.core_interfaces.domain import DocumentMetadata

class ArxivClient:
    """Fetches and parses Atom XML from the arXiv export API."""

    async def fetch_papers_by_query(
        self, query: str, limit: int = 5
    ) -> AsyncGenerator[DocumentMetadata, None]:

        url = "https://export.arxiv.org/api/query"
        # httpx automatically handles URL encoding (spaces to %20, etc.)
        query_params: dict[str, str | int] = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": limit
        }

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url=url, params=query_params)
            response.raise_for_status()

        # 1. Parse the string into an Abstract Syntax Tree (AST) in memory
        # Parse the raw XML into a Python AST
        root = ET.fromstring(response.text)

        # 2. Handle Namespaces (The "Messy" part)
        # XML Namespaces required to traverse the Atom feed
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        # 3. Traverse the tree to find 'entries' (papers)
        for entry in root.findall('atom:entry', ns):
            # Extract and clean the strings (removing newline entropy)
            title_elem = entry.find('atom:title', ns)
            abstract_elem = entry.find('atom:summary', ns)

            title = title_elem.text.strip().replace('\n', ' ') if title_elem is not None and title_elem.text else "Unknown"
            abstract = abstract_elem.text.strip().replace('\n', ' ') if abstract_elem is not None and abstract_elem.text else "No abstract."

            yield DocumentMetadata(id=uuid4(), title=title, abstract=abstract)
