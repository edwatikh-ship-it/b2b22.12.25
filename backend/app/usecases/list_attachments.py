from app.domain.ports import AttachmentRepositoryPort


class ListAttachmentsUseCase:
    def __init__(self, repo: AttachmentRepositoryPort) -> None:
        self._repo = repo

    async def execute(self, *, limit: int, offset: int) -> dict:
        return await self._repo.list(limit=limit, offset=offset)
