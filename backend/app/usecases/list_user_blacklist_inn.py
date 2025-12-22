from app.domain.ports import UserBlacklistInnRepositoryPort


class ListUserBlacklistInnUseCase:
    def __init__(self, repo: UserBlacklistInnRepositoryPort):
        self._repo = repo

    async def execute(self, user_id: int, limit: int) -> list[dict]:
        return await self._repo.list_inns(user_id=user_id, limit=limit)
