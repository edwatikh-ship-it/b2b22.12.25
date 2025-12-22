"""Moderator pending domains (from parsing_storage).
SSoT: api-contracts.yaml pending-domains."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter

from app.adapters import parsing_storage
from app.transport.schemas.moderator_pending_domains import (
    PendingDomainDetailDTO,
    PendingDomainDTO,
    PendingDomainListResponseDTO,
    PendingDomainUrlDTO,
)

router = APIRouter(tags=["ModeratorPendingDomains"])


@router.get("/moderator/pending-domains", response_model=PendingDomainListResponseDTO)
def list_pending_domains(
    limit: int = 50,
    offset: int = 0,
    sortBy: Literal["hits", "createdat", "domain"] = "hits",
    sortOrder: Literal["asc", "desc"] = "desc",
) -> PendingDomainListResponseDTO:
    print("DEBUG: START pending_domains, _runs len:", len(parsing_storage._runs))
    all_domains = set()
    for _run_id, run_data in parsing_storage._runs.items():
        for _kid, kdata in run_data["keys"].items():
            if kdata["status"] == "succeeded":
                for item in kdata["items"]:
                    all_domains.add(item["domain"])

    domains = sorted(list(all_domains))
    # MOCK PendingDomainDTO для Pydantic
    items = [
        PendingDomainDTO(
            domain=d,
            totalhits=1,
            urlcount=1,
            firstseenat="2025-12-20T19:53:00Z",
            lasthitat="2025-12-20T20:00:00Z",
            urls=[PendingDomainUrlDTO(url=f"https://{d}", hitcount=1, keys=["key1"])],
        )
        for d in domains[offset : offset + limit]
    ]

    print(f"DEBUG: returning {len(items)} domains")
    return PendingDomainListResponseDTO(items=items, limit=limit, offset=offset, total=len(domains))


@router.get("/moderator/pending-domains/{domain}", response_model=PendingDomainDetailDTO)
def get_pending_domain_detail(domain: str) -> PendingDomainDetailDTO:
    return PendingDomainDetailDTO(
        domain=domain,
        totalhits=5,
        urlcount=1,
        firstseenat="2025-12-20T19:53:00Z",
        lasthitat="2025-12-20T20:00:00Z",
        urls=[PendingDomainUrlDTO(url=f"https://{domain}", hitcount=5, keys=["key1"])],
    )
