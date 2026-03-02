"""
arXiv API Adapter.
Implements the AcademicGraphPort Protocol.
"""
import httpx
import xml.etree.ElementTree as ET
import uuid
from typing import AsyncGenerator
from datetime import datetime

from semantic_engine.core_interfaces.domain import DocumentMetadata
from semantic_engine.core_interfaces.api import AcademicGraphPort

class ArxivClient:
    """Fetches and parses Atom XML from the arXiv export API."""

    async def fetch_papers_by_query(
        self, query: str, limit: int = 5
    ) -> AsyncGenerator[DocumentMetadata, None]:

        url = "https://export.arxiv.org/api/query"
        query_params: dict[str, str | int] = {
            "search_query": query,
            "start": 0,
            "max_results": limit,
            "sortBy": "submittedDate", # Force arXiv to sort by time
            "sortOrder": "descending"
        }

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url=url, params=query_params)
            response.raise_for_status()

        # Parse the string into an Abstract Syntax Tree (AST) in memory
        # Parse the raw XML into a Python AST
        root = ET.fromstring(response.text)

        # Handle Namespaces (The "Messy" part)
        # XML Namespaces required to traverse the Atom feed
        ns = {'atom': 'http://www.w3.org/2005/Atom',
              'arxiv': 'http://arxiv.org/schemas/atom'}

        #  Traverse the XML tree to find 'entries' (papers)
        for entry in root.findall('atom:entry', ns):
            # 1. Base Text
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ') # type: ignore
            abstract = entry.find('atom:summary', ns).text.strip().replace('\n', ' ') # type: ignore
            # 2. Extract arXiv ID (The ID comes back as a URL, so we split it to get the raw ID)
            id_url = entry.find('atom:id', ns).text # type: ignore
            arxiv_id = id_url.split('/abs/')[-1] if id_url else None
            # 3. Extract Published Date
            published_str = entry.find('atom:published', ns).text # type: ignore
            # arXiv format: 2025-12-11T10:23:39Z
            published_date = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ") if published_str else None
            # 4. Extract Categories (Can be multiple)
            categories = [cat.attrib['term'] for cat in entry.findall('atom:category', ns)]

            # 5. Extract Authors (Can be multiple)
            authors = []
            author_orcids : dict[str,str|None] = {}
            for author_node in entry.findall('atom:author', ns):
                name_node = author_node.find('atom:name', ns)
                if name_node is not None and name_node.text is not None:
                    name = name_node.text.strip()
                    authors.append(name)

            # Yield the fully populated Domain particle
            yield DocumentMetadata(
                id=uuid.uuid4(),
                title=title,
                abstract=abstract,
                arxiv_id=arxiv_id,
                published_date=published_date,
                categories=categories,
                authors=authors,
                author_orcids=author_orcids
            )
