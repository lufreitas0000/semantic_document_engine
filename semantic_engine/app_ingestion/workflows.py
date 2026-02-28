"""
Application Layer Workflows.
It imports the Interfaces, but knows nothing about HTTP or SQL.
Coordinates the fetching of data from API ports and the storage of data
via the Unit of Work. Contains ZERO infrastructure logic.
"""
from semantic_engine.core_interfaces.api import AcademicGraphPort
from semantic_engine.core_interfaces.uow import AbstractUnitOfWork

async def fetch_and_store_papers(
    query: str,
    api_client: AcademicGraphPort, # Dependency Injection (Port)
    uow: AbstractUnitOfWork,       # Dependency Injection (Port)
    limit: int = 5
) -> int:
    """
    The orchestrator. It streams particles from the API and commits them
    atomically to the database.
    """
    papers_saved = 0

    # 1. Ask the Port for data
    async for document in api_client.fetch_papers_by_query(query, limit):
        # 2. Open an atomic database transaction
        with uow:
            uow.documents.add(document)
            uow.commit()

        papers_saved += 1

    return papers_saved
