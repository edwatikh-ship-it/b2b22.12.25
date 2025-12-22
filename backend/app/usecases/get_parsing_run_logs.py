"""
Get parsing run logs usecase - real DB implementation.
"""

import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import ParsingRepository
from app.transport.schemas.moderator_parsing_logs import (
    ParsingRunEventDTO,
    ParsingRunEventLevel,
    ParsingRunLogResponseDTO,
)


async def get_parsing_run_logs(
    run_id: str,
    session: AsyncSession,
) -> ParsingRunLogResponseDTO:
    """
    Get logs for a parsing run from DB.
    """
    parsing_repo = ParsingRepository(session)
    
    # Get runs by prefix
    runs = await parsing_repo.get_parsing_runs_by_prefix(run_id)
    if not runs:
        raise ValueError(f"No runs found for runId {run_id}")
    
    # Collect logs from all matching runs
    all_events = []
    for run in runs:
        logs = await parsing_repo.get_logs_by_run_id(run.id)
        for log in logs:
            # Parse context if it's JSON string
            context = None
            if log.context:
                try:
                    context = json.loads(log.context)
                except (json.JSONDecodeError, TypeError):
                    context = {"raw": log.context}
            
            all_events.append(
                ParsingRunEventDTO(
                    timestamp=log.timestamp,
                    level=ParsingRunEventLevel(log.level),
                    message=log.message,
                    context=context,
                )
            )
    
    # Sort by timestamp
    all_events.sort(key=lambda e: e.timestamp)
    
    return ParsingRunLogResponseDTO(
        runId=run_id,
        events=all_events,
    )
