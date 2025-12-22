from __future__ import annotations

from typing import Protocol

from app.domain.models.user_blacklist_inn import UserBlacklistInnItem


class UserBlacklistInnRepositoryPort(Protocol):
    async def add_inn(self, *, user_id: int, inn: str, reason: str | None) -> None: ...

    async def list_inn(self, *, user_id: int, limit: int) -> list[UserBlacklistInnItem]: ...

    async def remove_inn(self, *, user_id: int, inn: str) -> None: ...
