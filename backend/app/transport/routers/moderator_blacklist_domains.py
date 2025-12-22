from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import DomainBlacklistRepository
from app.adapters.db.session import getdbsession
from app.transport.schemas.moderator_blacklist_domains import (
    AddModeratorBlacklistDomainRequestDTO,
    ModeratorBlacklistDomainDTO,
    ModeratorBlacklistDomainListResponseDTO,
)

router = APIRouter(tags=["Blacklist"])


def _iso(dt: object) -> str:
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.isoformat()
    return str(dt)


@router.post("/moderator/blacklist/domains", response_model=ModeratorBlacklistDomainDTO)
async def add_blacklist_domain(
    payload: AddModeratorBlacklistDomainRequestDTO,
    session: AsyncSession = Depends(getdbsession),
) -> ModeratorBlacklistDomainDTO:
    repo = DomainBlacklistRepository(session)
    try:
        # add_root_domain returns domain id (and may update comment on re-add)
        domain_id = await repo.add_root_domain(payload.domain, comment=payload.comment)
    except TypeError:
        # fallback for older signature without comment/return id
        await repo.add_root_domain(payload.domain)
        # best-effort: fetch id via list_domains (latest matching root_domain)
        rows = await repo.list_domains(limit=1, offset=0)
        domain_id = next((row[0] for row in rows if row[1] == payload.domain.strip().lower()), None)
        if domain_id is None:
            raise HTTPException(
                status_code=500, detail="Failed to resolve domain_id after add_root_domain"
            )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    if payload.url:
        await repo.add_domain_urls(
            domain_id=int(domain_id), urls=[str(payload.url)], comment=payload.comment
        )

    # Return actual stored urls (url/comment/created_at)
    url_rows = await repo.get_domain_urls(int(domain_id))
    urls = [
        {"url": u, "comment": uc, "createdat": _iso(u_ca)} for (u, uc, u_ca) in (url_rows or [])
    ]

    return ModeratorBlacklistDomainDTO(
        domain=payload.domain.strip().lower(),
        createdat=_iso(datetime.now(tz=UTC)),
        comment=payload.comment,
        urls=urls,
    )


@router.get("/moderator/blacklist/domains", response_model=ModeratorBlacklistDomainListResponseDTO)
async def list_blacklist_domains(
    limit: int = 200,
    offset: int = 0,
    session: AsyncSession = Depends(getdbsession),
) -> ModeratorBlacklistDomainListResponseDTO:
    repo = DomainBlacklistRepository(session)

    if hasattr(repo, "list_domains") and hasattr(repo, "count_domains"):
        total = await repo.count_domains()
        rows = await repo.list_domains(limit=limit, offset=offset)
        items = []
        for row in rows:
            # repo.list_domains returns: (id, rootdomain, createdat, comment)
            d = row[1]
            ca = row[2] if len(row) > 2 else datetime.now(tz=UTC)
            c = row[3] if len(row) > 3 else None
            url_rows = await repo.get_domain_urls(row[0])
            urls = [
                {"url": u, "comment": uc, "createdat": _iso(u_ca)}
                for (u, uc, u_ca) in (url_rows or [])
            ]
            items.append(
                ModeratorBlacklistDomainDTO(domain=d, createdat=_iso(ca), comment=c, urls=urls)
            )
        return ModeratorBlacklistDomainListResponseDTO(
            items=items, limit=limit, offset=offset, total=total
        )

    # Fallback (legacy)
    domains = await repo.list_root_domains(limit=limit)
    items = [
        ModeratorBlacklistDomainDTO(
            domain=d, createdat=_iso(datetime.now(tz=UTC)), comment=None, urls=[]
        )
        for d in domains
    ]
    return ModeratorBlacklistDomainListResponseDTO(
        items=items, limit=limit, offset=0, total=len(items)
    )


@router.delete("/moderator/blacklist/domains/{domain}")
async def delete_blacklist_domain(
    domain: str,
    session: AsyncSession = Depends(getdbsession),
) -> None:
    repo = DomainBlacklistRepository(session)
    await repo.remove_root_domain(domain)
    return None
