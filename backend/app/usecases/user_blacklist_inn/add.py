from __future__ import annotations

from dataclasses import dataclass

from app.domain.blacklist_ports.user_blacklist_inn import UserBlacklistInnRepositoryPort


@dataclass(frozen=True, slots=True)
class AddUserBlacklistInnCommand:
    user_id: int
    inn: str
    reason: str | None


class AddUserBlacklistInnUseCase:
    def __init__(self, repo: UserBlacklistInnRepositoryPort) -> None:
        self._repo = repo

    async def execute(self, cmd: AddUserBlacklistInnCommand) -> None:
        await self._repo.add_inn(user_id=cmd.user_id, inn=cmd.inn, reason=cmd.reason)
