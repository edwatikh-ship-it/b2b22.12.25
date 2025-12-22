"""
List keywords base usecase - real DB implementation.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.adapters.db.models import (
    DomainBlacklistDomainModel,
    ParsingHitModel,
    ParsingRunModel,
    RequestKeyModel,
)
from app.transport.schemas.moderator_keywords import (
    KeywordItemDTO,
    KeywordStatus,
    KeywordsListResponseDTO,
)


async def list_keywords(
    session: AsyncSession,
    q: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    sort: str = "keyword_asc",
) -> KeywordsListResponseDTO:
    """
    List all keywords from keywords base with real DB queries.
    Each keyword = one row from request_keys table.
    """
    # Get blacklisted domains for filtering
    blacklist_stmt = select(DomainBlacklistDomainModel.root_domain)
    blacklist_result = await session.execute(blacklist_stmt)
    blacklisted_domains = set(blacklist_result.scalars().all())
    
    # Base query for request_keys
    stmt = select(RequestKeyModel)
    
    # Apply text filter
    if q:
        stmt = stmt.where(RequestKeyModel.text.ilike(f"%{q}%"))
    
    # Count total before pagination
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await session.scalar(count_stmt) or 0
    
    # Apply sorting
    if sort == "keyword_desc":
        stmt = stmt.order_by(RequestKeyModel.text.desc())
    elif sort == "created_at_desc":
        stmt = stmt.order_by(RequestKeyModel.id.desc())
    elif sort == "created_at_asc":
        stmt = stmt.order_by(RequestKeyModel.id.asc())
    else:  # keyword_asc
        stmt = stmt.order_by(RequestKeyModel.text.asc())
    
    # Apply pagination
    stmt = stmt.limit(limit).offset(offset)
    
    result = await session.execute(stmt)
    keys = list(result.scalars().all())
    
    # Build response items with parsing info
    items = []
    for key in keys:
        # Find last parsing run for this key
        last_run_stmt = (
            select(ParsingRunModel)
            .join(ParsingHitModel, ParsingRunModel.id == ParsingHitModel.run_id)
            .where(ParsingHitModel.key_id == key.id)
            .order_by(ParsingRunModel.created_at.desc())
            .limit(1)
        )
        last_run_result = await session.execute(last_run_stmt)
        last_run = last_run_result.scalars().first()
        
        # Compute status
        if last_run:
            if last_run.status == "succeeded":
                computed_status = KeywordStatus.parsed
            elif last_run.status == "failed":
                computed_status = KeywordStatus.failed
            else:
                computed_status = KeywordStatus.pending
        else:
            computed_status = KeywordStatus.pending
        
        # Apply status filter
        if status and computed_status.value != status:
            continue
        
        # Count unique domains for this key (excluding blacklist)
        domains_count = 0
        if last_run:
            domains_stmt = (
                select(func.count(func.distinct(ParsingHitModel.domain)))
                .where(ParsingHitModel.key_id == key.id)
            )
            if blacklisted_domains:
                domains_stmt = domains_stmt.where(
                    ~ParsingHitModel.domain.in_(blacklisted_domains)
                )
            domains_count = await session.scalar(domains_stmt) or 0
        
        items.append(
            KeywordItemDTO(
                keyId=key.id,
                requestId=key.request_id,
                keyword=key.text,
                status=computed_status,
                lastRunId=last_run.run_id if last_run else None,
                lastRunStatus=last_run.status if last_run else None,
                lastRunAt=last_run.created_at if last_run else None,
                domainsFound=domains_count,
            )
        )
    
    return KeywordsListResponseDTO(
        items=items,
        limit=limit,
        offset=offset,
        total=total,
    )
