from __future__ import annotations

from dataclasses import dataclass

from app.domain.blacklist_ports.user_blacklist_inn import UserBlacklistInnRepositoryPort
from app.domain.models.user_blacklist_inn import UserBlacklistInnItem


@dataclass(frozen=True, slots=True)
class ListUserBlacklistInnQuery:
    user_id: int
    limit: int


class ListUserBlacklistInnUseCase:
    def __init__(self, repo: UserBlacklistInnRepositoryPort) -> None:
        self._repo = repo

    async def execute(self, q: ListUserBlacklistInnQuery) -> list[UserBlacklistInnItem]:
        return await self._repo.list_inn(user_id=q.user_id, limit=q.limit)
