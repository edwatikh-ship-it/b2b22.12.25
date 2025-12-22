from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class UserBlacklistInnItem:
    id: int
    inn: str
    supplier_id: int | None
    supplier_name: str | None
    checko_data: dict[str, Any] | None
    reason: str | None
    created_at: datetime
