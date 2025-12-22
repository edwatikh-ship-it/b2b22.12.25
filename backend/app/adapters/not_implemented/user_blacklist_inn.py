from __future__ import annotations

from app.domain.blacklist_ports.user_blacklist_inn import UserBlacklistInnRepositoryPort


class NotImplementedUserBlacklistInnRepository(UserBlacklistInnRepositoryPort):
    async def add_inn(self, *, user_id: int, inn: str, reason: str | None) -> None:
        raise NotImplementedError("User blacklist by INN repository is not implemented yet")

    async def list_inn(self, *, user_id: int, limit: int):
        raise NotImplementedError("User blacklist by INN repository is not implemented yet")

    async def remove_inn(self, *, user_id: int, inn: str) -> None:
        raise NotImplementedError("User blacklist by INN repository is not implemented yet")
