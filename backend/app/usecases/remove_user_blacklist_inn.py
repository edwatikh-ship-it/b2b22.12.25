from app.domain.ports import UserBlacklistInnRepositoryPort


class RemoveUserBlacklistInnUseCase:
    def __init__(self, repo: UserBlacklistInnRepositoryPort):
        self._repo = repo

    async def execute(self, user_id: int, inn: str) -> None:
        await self._repo.remove_inn(user_id=user_id, inn=inn)
