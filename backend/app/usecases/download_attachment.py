from app.adapters.storage.filestorage import LocalAttachmentStorage
from app.domain.ports import AttachmentRepositoryPort


class DownloadAttachmentUseCase:
    def __init__(self, repo: AttachmentRepositoryPort, storage: LocalAttachmentStorage) -> None:
        self._repo = repo
        self._storage = storage

    async def execute(self, attachment_id: int) -> tuple[dict, bytes] | None:
        meta = await self._repo.get(attachment_id)
        if meta is None:
            return None
        if not meta.get("storagekey"):
            return None
        content = self._storage.read(storage_key=meta["storagekey"])
        return meta, content
