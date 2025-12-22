"""
List parsing runs usecase.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import ParsingRepository
from app.transport.schemas.moderator_parsing import (
    ParsingKeyStatusDTO,
    ParsingRunStatus,
    ParsingStatusResponseDTO,
)


async def list_parsing_runs(
    session: AsyncSession,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """
    List parsing runs from DB.
    Returns list of runs with basic info (no external API calls).
    """
    parsing_repo = ParsingRepository(session)
    runs = await parsing_repo.list_parsing_runs(limit=limit, offset=offset)

    result = []
    for run in runs:
        result.append({
            "runId": run.run_id,
            "requestId": run.request_id,
            "status": run.status,
            "depth": run.depth,
            "source": run.source,
            "createdAt": run.created_at.isoformat() if run.created_at else None,
            "finishedAt": run.finished_at.isoformat() if run.finished_at else None,
            "errorMessage": run.error_message,
        })

    return result
