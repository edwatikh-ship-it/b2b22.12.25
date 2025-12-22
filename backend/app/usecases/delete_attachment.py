from app.domain.ports import AttachmentRepositoryPort


class DeleteAttachmentUseCase:
    def __init__(self, repo: AttachmentRepositoryPort) -> None:
        self._repo = repo

    async def execute(self, attachment_id: int) -> None:
        await self._repo.soft_delete(attachment_id)
