from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import DomainDecisionRepository
from app.adapters.db.session import getdbsession
from app.transport.schemas.moderator_domain_decision import (
    DomainDecisionRequestDTO,
    DomainDecisionResponseDTO,
)

router = APIRouter(tags=["ModeratorDomainDecision"])


def _iso(dt: object) -> str:
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.isoformat()
    return str(dt)


@router.get(
    "/moderator/domains/{domain}/decision",
    response_model=DomainDecisionResponseDTO,
    responses={404: {"description": "Domain not found or no decision made"}},
)
async def get_domain_decision(
    domain: str,
    session: AsyncSession = Depends(getdbsession),
) -> DomainDecisionResponseDTO:
    repo = DomainDecisionRepository(session)
    row = await repo.get_by_domain(domain)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found or no decision made",
        )

    return DomainDecisionResponseDTO(
        domain=row.domain,
        status=row.status,
        decisionat=_iso(row.updated_at or row.created_at),
        supplierid=None,
        card=None,
        comment=row.comment,
        urls=[],
    )


@router.post(
    "/moderator/domains/{domain}/decision",
    response_model=DomainDecisionResponseDTO,
    responses={404: {"description": "Domain not found"}},
)
async def make_domain_decision(
    domain: str,
    body: DomainDecisionRequestDTO,
    session: AsyncSession = Depends(getdbsession),
) -> DomainDecisionResponseDTO:
    if body.status in ("supplier", "reseller") and body.carddata is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="carddata is required for status supplier/reseller",
        )

    repo = DomainDecisionRepository(session)
    row = await repo.upsert(
        domain=domain,
        status=body.status.value,
        comment=body.comment,
        carddata=body.carddata.model_dump() if body.carddata else None,
    )

    return DomainDecisionResponseDTO(
        domain=row.domain,
        status=row.status,
        decisionat=_iso(row.updated_at or row.created_at),
        supplierid=None,
        card=None,
        comment=row.comment,
        urls=[],
    )
