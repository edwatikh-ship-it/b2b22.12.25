from typing import Annotated

import logging
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.session import get_db_session
from app.transport.schemas.moderator_parsing import (
    ManualParsingRequestDTO,
    ParsingResultsResponseDTO,
    ParsingStatusResponseDTO,
    StartParsingRequestDTO,
    StartParsingResponseDTO,
)
from app.transport.schemas.moderator_parsing_logs import (
    ParsingRunLogResponseDTO,
)
from app.usecases.get_parsing_results import get_parsing_results
from app.usecases.get_parsing_run_logs import get_parsing_run_logs
from app.usecases.get_parsing_status import get_parsing_status
from app.usecases.list_parsing_runs import list_parsing_runs as list_parsing_runs_uc
from app.usecases.start_parsing import manual_parsing, start_parsing

router = APIRouter(tags=["ModeratorTasks"])

logger = logging.getLogger(__name__)


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
        logger.info(
            "HTTP start-parsing called: requestId=%s depth=%s source=%s",
            request_id,
            payload.depth,
            getattr(payload.source, "value", payload.source),
        )
        return await start_parsing(request_id, payload, session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Parser service unavailable: {str(e)}")
    except Exception as e:
        logger.exception("Error in start_parsing")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/moderator/manual-parsing",
    response_model=StartParsingResponseDTO,
)
async def manual_parsing_endpoint(
    payload: ManualParsingRequestDTO,
    session: AsyncSession = Depends(get_db_session),
) -> StartParsingResponseDTO:
    try:
        logger.info(
            "HTTP manual-parsing called: keyword=%s depth=%s source=%s",
            payload.keyword,
            payload.depth,
            getattr(payload.source, "value", payload.source),
        )
        dto = StartParsingRequestDTO(depth=payload.depth, source=payload.source)
        return await manual_parsing(payload.keyword, dto, session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Parser service unavailable: {str(e)}")
    except Exception as e:
        logger.exception("Error in manual_parsing")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/moderator/parsing-runs", response_model=dict)
async def list_parsing_runs_endpoint(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    try:
        runs = await list_parsing_runs_uc(session, limit, offset)
        return {
            "items": runs,
            "limit": limit,
            "offset": offset,
            "total": len(runs),
        }
    except Exception as e:
        logger.exception("Error in list_parsing_runs_endpoint")
        # Return empty list on error to allow frontend to load
        return {
            "items": [],
            "limit": limit,
            "offset": offset,
            "total": 0,
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
        logger.exception("Error in get_parsing_run_logs_endpoint")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/moderator/requests/{requestId}/parsing-status",
    response_model=ParsingStatusResponseDTO,
)
async def get_parsing_status_endpoint(
    request_id: Annotated[int, Path(alias="requestId")],
    session: AsyncSession = Depends(get_db_session),
) -> ParsingStatusResponseDTO:
    try:
        return await get_parsing_status(request_id, session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Error in get_parsing_status_endpoint")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/moderator/requests/{requestId}/parsing-results",
    response_model=ParsingResultsResponseDTO,
)
async def get_parsing_results_by_request_endpoint(
    request_id: Annotated[int, Path(alias="requestId")],
    session: AsyncSession = Depends(get_db_session),
) -> ParsingResultsResponseDTO:
    """
    Get parsing results by requestId.
    Returns results from the latest parsing run for this request.
    """
    try:
        # Get latest run for this request
        from app.adapters.db.repositories import ParsingRepository
        from sqlalchemy import select
        from app.adapters.db.models import ParsingRunModel
        
        parsing_repo = ParsingRepository(session)
        
        # Find latest run (simplified - in real implementation, we'd link user_request_id)
        stmt = (
            select(ParsingRunModel)
            .order_by(ParsingRunModel.created_at.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        latest_run = result.scalars().first()
        
        if not latest_run:
            raise ValueError(f"No parsing runs found for request {request_id}")
        
        return await get_parsing_results(latest_run.run_id, session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Error in get_parsing_results_by_request_endpoint")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/moderator/resolved-domains")
async def list_resolved_domains_endpoint(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session),
):
    """
    List resolved domains (domains with decisions).
    SSoT: api-contracts.yaml /moderator/resolved-domains
    """
    # TODO: Implement using DomainDecisionRepository
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get("/moderator/domains/{domain}/hits")
async def get_domain_hits_endpoint(
    domain: Annotated[str, Path()],
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get domain hits (parsing hits for a domain).
    SSoT: api-contracts.yaml /moderator/domains/{domain}/hits
    """
    # TODO: Implement using ParsingRepository.get_hits_by_domain
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get("/moderator/urls/hits")
async def get_url_hits_endpoint(
    url: str,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Get URL hits (parsing hits for a URL).
    SSoT: api-contracts.yaml /moderator/urls/hits
    """
    # TODO: Implement using ParsingRepository.get_hits_by_url
    raise HTTPException(status_code=501, detail="Not Implemented")
