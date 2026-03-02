"""
Application Layer Workflows.
It imports the Interfaces, but knows nothing about HTTP or SQL.
Coordinates the fetching of data from API ports and the storage of data
via the Unit of Work. Contains ZERO infrastructure logic.
"""
from dataclasses import replace

from semantic_engine.core_interfaces.api import AcademicGraphPort
from semantic_engine.core_interfaces.uow import AbstractUnitOfWork
from semantic_engine.core_interfaces.ml import TextEmbeddingPort
from semantic_engine.core_interfaces.domain import DocumentMetadata

async def fetch_and_store_papers(
    query: str,
    api_client: AcademicGraphPort, # Dependency Injection (Port)
    uow: AbstractUnitOfWork,       # Dependency Injection (Port)
    ml_model: TextEmbeddingPort,
    limit: int = 5
) -> int:
    """
    The orchestrator. It streams particles from the API and commits them
    atomically to the database.
    """
    papers_saved = 0
    with uow:
        async for document in api_client.fetch_papers_by_query(query, limit):
            # 1. Project text into embedding manifold (R^n)
            vector = ml_model.embed_text(document.abstract)

            # 2. Allocate new PyObject via functional replacement
            #    (Dynamic hardware routing based on tensor shape)
            if len(vector) == 768:
                embedded_document = replace(document, embedding_scibert=vector)
            elif len(vector) == 384:
                embedded_document = replace(document, embedding=vector)
            else:
                raise ValueError(
                    f"Vector manifold mismatch: expected R^384 or R^768, got R^{len(vector)}"
                )

            # 3. Add to Unit of Work (Heap memory)
            uow.documents.add(embedded_document)
            papers_saved += 1

        # Flush Heap memory buffer to Disk (ACID transaction)
        uow.commit()

    return papers_saved


async def search_papers(
    query: str,
    ml_model: TextEmbeddingPort,
    uow: AbstractUnitOfWork,
    limit: int = 5
) -> list[tuple[DocumentMetadata, float]]:
    """
    The orchestrator for semantic search.
    Translates text into math, and searches the database.
    """
    # 1. Translate the human language into a mathematical vector
    query_vector = ml_model.embed_text(query)

    # 2. Open an atomic read transaction and execute the search
    with uow:
        results = uow.documents.search_by_embedding(query_embedding=query_vector, limit=limit)

    return results
