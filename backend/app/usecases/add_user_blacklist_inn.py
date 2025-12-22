from app.domain.ports import UserBlacklistInnRepositoryPort


class AddUserBlacklistInnUseCase:
    def __init__(self, repo: UserBlacklistInnRepositoryPort):
        self._repo = repo

    async def execute(self, user_id: int, inn: str, reason: str | None) -> None:
        await self._repo.add_inn(user_id=user_id, inn=inn, reason=reason)
