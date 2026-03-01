"""
Integration tests for the arXiv Adapter using VCR to freeze network entropy.
"""
import pytest
import vcr  # type: ignore
from semantic_engine.infrastructure.api.arxiv import ArxivClient

# Configure VCR to filter out sensitive headers if we had API keys
my_vcr = vcr.VCR(
    cassette_library_dir='semantic_engine/tests/cassettes',
    record_mode='once',
    match_on=['method', 'scheme', 'host', 'port', 'path', 'query'],
)

@pytest.mark.anyio
@my_vcr.use_cassette('arxiv_quantum_query.yaml')
async def test_arxiv_client_fetches_and_parses_xml_correctly() -> None:
    client = ArxivClient()

    # We use a list comprehension to exhaust the AsyncGenerator
    papers = [paper async for paper in client.fetch_papers_by_query("quantum", limit=2)]

    # Mathematical proof of adapter success
    assert len(papers) == 2
    assert "quantum" in papers[0].title.lower() or "quantum" in papers[0].abstract.lower()

    # Prove the XML newlines were cleaned
    assert "\n" not in papers[0].title
