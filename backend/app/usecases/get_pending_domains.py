"""
Get pending domains usecase.
SSoT: api-contracts.yaml /moderator/pending-domains
"""

from datetime import datetime
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import ParsingRepository
from app.transport.schemas.moderator_pending_domains import (
    PendingDomainDTO,
    PendingDomainDetailDTO,
    PendingDomainListResponseDTO,
    PendingDomainUrlDTO,
)


async def list_pending_domains(
    session: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    sort_by: Literal["hits", "createdat", "domain"] = "hits",
    sort_order: Literal["asc", "desc"] = "desc",
) -> PendingDomainListResponseDTO:
    """
    List pending domains (domains that are not blacklisted and have no decision).
    """
    parsing_repo = ParsingRepository(session)
    
    try:
        domains_data = await parsing_repo.get_pending_domains(
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        
        # Get total count (without limit/offset)
        total_data = await parsing_repo.get_pending_domains(
            limit=10000,  # Large limit to get all
            offset=0,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        total = len(total_data)
        
        items = []
        for domain, total_hits, url_count, first_seen_at, last_hit_at in domains_data:
            # Get URLs for this domain (simplified - just one URL per domain for now)
            # In full implementation, we'd fetch all URLs
            items.append(
                PendingDomainDTO(
                    domain=domain,
                    totalhits=total_hits,
                    urlcount=url_count,
                    firstseenat=first_seen_at.isoformat() if isinstance(first_seen_at, datetime) else str(first_seen_at),
                    lasthitat=last_hit_at.isoformat() if isinstance(last_hit_at, datetime) else str(last_hit_at),
                    urls=[],  # Will be populated in detail endpoint
                )
            )
        
        return PendingDomainListResponseDTO(
            items=items,
            limit=limit,
            offset=offset,
            total=total,
        )
    except Exception as e:
        # Return empty list on error
        return PendingDomainListResponseDTO(
            items=[],
            limit=limit,
            offset=offset,
            total=0,
        )


async def get_pending_domain_detail(
    session: AsyncSession,
    domain: str,
) -> PendingDomainDetailDTO:
    """
    Get pending domain detail with URLs and keywords.
    """
    parsing_repo = ParsingRepository(session)
    
    try:
        domain_data = await parsing_repo.get_pending_domain_detail(domain)
        domain_name, total_hits, url_count, first_seen_at, last_hit_at, url_list = domain_data
        
        urls = [
            PendingDomainUrlDTO(
                url=url,
                hitcount=hit_count,
                keys=list(set(keywords)),  # Unique keywords
            )
            for url, hit_count, keywords in url_list
        ]
        
        return PendingDomainDetailDTO(
            domain=domain_name,
            totalhits=total_hits,
            urlcount=url_count,
            firstseenat=first_seen_at.isoformat() if isinstance(first_seen_at, datetime) else str(first_seen_at),
            lasthitat=last_hit_at.isoformat() if isinstance(last_hit_at, datetime) else str(last_hit_at),
            urls=urls,
        )
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(f"Failed to get pending domain detail: {str(e)}")




