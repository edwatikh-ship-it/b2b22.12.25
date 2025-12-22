"""Moderator blacklist domains DTOs.

SSoT: api-contracts.yaml
- AddModeratorBlacklistDomainRequestDTO
- ModeratorBlacklistUrlItemDTO
- ModeratorBlacklistDomainDTO
- ModeratorBlacklistDomainListResponseDTO
"""

from __future__ import annotations

from pydantic import AnyUrl, BaseModel, Field


class AddModeratorBlacklistDomainRequestDTO(BaseModel):
    domain: str = Field(..., min_length=1)
    comment: str | None = None
    url: AnyUrl | None = None


class ModeratorBlacklistUrlItemDTO(BaseModel):
    url: AnyUrl
    comment: str | None = None
    createdat: str


class ModeratorBlacklistDomainDTO(BaseModel):
    domain: str
    createdat: str
    comment: str | None = None
    urls: list[ModeratorBlacklistUrlItemDTO]


class ModeratorBlacklistDomainListResponseDTO(BaseModel):
    items: list[ModeratorBlacklistDomainDTO]
    limit: int
    offset: int
    total: int


# Simple OK response (used by DELETE endpoints)
class GenericOkResponseDTO(BaseModel):
    success: bool = True
    message: str | None = None
