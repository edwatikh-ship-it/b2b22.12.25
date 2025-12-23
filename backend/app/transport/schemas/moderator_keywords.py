"""
Schemas for moderator keywords base.
SSoT: api-contracts.yaml
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict

from app.transport.schemas.moderator_parsing import ParsingRunStatus


class KeywordStatus(str, Enum):
    """Keyword status."""
    pending = "pending"
    parsed = "parsed"
    failed = "failed"


class KeywordItemDTO(BaseModel):
    """Single keyword item in the base."""
    model_config = ConfigDict(from_attributes=True)

    keyId: int
    requestId: int
    keyword: str
    status: KeywordStatus
    lastRunId: str | None = None  # Changed from int to str (UUID)
    lastRunStatus: ParsingRunStatus | None = None
    lastRunAt: datetime | None = None
    domainsFound: int


class KeywordsListResponseDTO(BaseModel):
    """Response with list of keywords."""
    model_config = ConfigDict(from_attributes=True)

    items: list[KeywordItemDTO]
    limit: int
    offset: int
    total: int
