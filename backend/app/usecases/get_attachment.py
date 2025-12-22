from app.domain.ports import AttachmentRepositoryPort


class GetAttachmentUseCase:
    def __init__(self, repo: AttachmentRepositoryPort) -> None:
        self._repo = repo

    async def execute(self, attachment_id: int) -> dict | None:
        return await self._repo.get(attachment_id)
