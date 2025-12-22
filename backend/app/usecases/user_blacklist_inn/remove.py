from __future__ import annotations

from dataclasses import dataclass

from app.domain.blacklist_ports.user_blacklist_inn import UserBlacklistInnRepositoryPort


@dataclass(frozen=True, slots=True)
class RemoveUserBlacklistInnCommand:
    user_id: int
    inn: str


class RemoveUserBlacklistInnUseCase:
    def __init__(self, repo: UserBlacklistInnRepositoryPort) -> None:
        self._repo = repo

    async def execute(self, cmd: RemoveUserBlacklistInnCommand) -> None:
        await self._repo.remove_inn(user_id=cmd.user_id, inn=cmd.inn)
