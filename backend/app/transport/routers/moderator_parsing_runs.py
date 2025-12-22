from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.session import get_db_session
from app.transport.schemas.moderator_parsing import (
    ParsingResultsResponseDTO,
    StartParsingRequestDTO,
    StartParsingResponseDTO,
)
from app.transport.schemas.moderator_parsing_logs import (
    ParsingRunLogResponseDTO,
)
from app.usecases.get_parsing_results import get_parsing_results
from app.usecases.get_parsing_run_logs import get_parsing_run_logs
from app.usecases.list_parsing_runs import list_parsing_runs as list_parsing_runs_uc
from app.usecases.start_parsing import start_parsing

router = APIRouter(tags=["ModeratorTasks"])


@router.post(
    "/moderator/requests/{requestId}/start-parsing",
    response_model=StartParsingResponseDTO,
)
async def start_parsing_endpoint(
    request_id: Annotated[int, Path(alias="requestId")],
    payload: StartParsingRequestDTO,
    session: AsyncSession = Depends(get_db_session),
) -> StartParsingResponseDTO:
    try:
        return await start_parsing(request_id, payload, session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/moderator/parsing-runs", response_model=dict)
async def list_parsing_runs_endpoint(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    runs = await list_parsing_runs_uc(session, limit, offset)
    return {
        "items": runs,
        "limit": limit,
        "offset": offset,
        "total": len(runs),
    }


@router.get(
    "/moderator/parsing-runs/{runId}",
    response_model=ParsingResultsResponseDTO,
)
async def get_parsing_run_detail(
    run_id: Annotated[str, Path(alias="runId")],
    session: AsyncSession = Depends(get_db_session),
) -> ParsingResultsResponseDTO:
    try:
        return await get_parsing_results(run_id, session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/moderator/parsing-runs/{runId}/logs")
async def get_parsing_run_logs_endpoint(
    run_id: Annotated[str, Path(alias="runId")],
    session: AsyncSession = Depends(get_db_session),
):
    from app.transport.schemas.moderator_parsing_logs import ParsingRunLogResponseDTO
    from app.usecases.get_parsing_run_logs import get_parsing_run_logs
    
    try:
        return await get_parsing_run_logs(run_id, session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
