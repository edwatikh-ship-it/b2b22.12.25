"""Moderator pending domains (from database).
SSoT: api-contracts.yaml pending-domains."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.session import get_db_session
from app.transport.schemas.moderator_pending_domains import (
    PendingDomainDetailDTO,
    PendingDomainListResponseDTO,
)
from app.usecases.get_pending_domains import (
    get_pending_domain_detail,
    list_pending_domains,
)

router = APIRouter(tags=["ModeratorPendingDomains"])


@router.get("/moderator/pending-domains", response_model=PendingDomainListResponseDTO)
async def list_pending_domains_endpoint(
    limit: int = 50,
    offset: int = 0,
    sortBy: Literal["hits", "createdat", "domain"] = "hits",
    sortOrder: Literal["asc", "desc"] = "desc",
    session: AsyncSession = Depends(get_db_session),
) -> PendingDomainListResponseDTO:
    try:
        return await list_pending_domains(session, limit, offset, sortBy, sortOrder)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Error in list_pending_domains_endpoint")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/moderator/pending-domains/{domain}", response_model=PendingDomainDetailDTO)
async def get_pending_domain_detail_endpoint(
    domain: Annotated[str, Path()],
    session: AsyncSession = Depends(get_db_session),
) -> PendingDomainDetailDTO:
    try:
        return await get_pending_domain_detail(session, domain)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Error in get_pending_domain_detail_endpoint")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
