from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class PendingDomainUrlDTO(BaseModel):
    url: str
    hitcount: int
    keys: list[str]


class PendingDomainDTO(BaseModel):
    domain: str
    totalhits: int
    urlcount: int
    firstseenat: datetime
    lasthitat: datetime
    urls: list[PendingDomainUrlDTO]


class PendingDomainDetailDTO(BaseModel):
    domain: str
    totalhits: int
    urlcount: int
    firstseenat: datetime
    lasthitat: datetime
    urls: list[PendingDomainUrlDTO]


class PendingDomainListResponseDTO(BaseModel):
    items: list[PendingDomainDTO]
    limit: int
    offset: int
    total: int
