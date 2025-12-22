from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AddUserBlacklistInnRequestDTO(BaseModel):
    inn: str = Field(min_length=10, max_length=12)
    reason: str | None = None


class UserBlacklistInnItemDTO(BaseModel):
    id: int
    inn: str
    supplier_id: int | None = None
    supplier_name: str | None = None
    checko_data: dict[str, Any] | None = None
    reason: str | None = None
    created_at: datetime


class UserBlacklistInnListResponseDTO(BaseModel):
    items: list[UserBlacklistInnItemDTO]
