from app.adapters.storage.filestorage import LocalAttachmentStorage
from app.domain.ports import AttachmentRepositoryPort


class UploadAttachmentUseCase:
    def __init__(self, repo: AttachmentRepositoryPort, storage: LocalAttachmentStorage) -> None:
        self._repo = repo
        self._storage = storage

    async def execute(
        self, *, title: str | None, original_filename: str, content_type: str | None, content: bytes
    ) -> dict:
        stored = self._storage.save(original_filename=original_filename, content=content)
        return await self._repo.create(
            title=title,
            original_filename=original_filename,
            content_type=content_type,
            size_bytes=stored.size_bytes,
            sha256=stored.sha256,
            storage_key=stored.storage_key,
        )
