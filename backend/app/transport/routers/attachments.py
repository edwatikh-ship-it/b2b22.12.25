from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import AttachmentRepository
from app.adapters.db.session import get_db_session
from app.adapters.storage.filestorage import LocalAttachmentStorage
from app.transport.schemas.attachments import (
    AttachmentDTO,
    AttachmentListResponseDTO,
    GenericOkResponseDTO,
)
from app.usecases.delete_attachment import DeleteAttachmentUseCase
from app.usecases.download_attachment import DownloadAttachmentUseCase
from app.usecases.get_attachment import GetAttachmentUseCase
from app.usecases.list_attachments import ListAttachmentsUseCase
from app.usecases.upload_attachment import UploadAttachmentUseCase

router = APIRouter(prefix="/user/attachments", tags=["Attachments"])


def storage() -> LocalAttachmentStorage:
    return LocalAttachmentStorage(base_dir=Path("storage/attachments"))


def _map_attachment_to_dto(data: dict) -> AttachmentDTO:
    # usecases/adapters Р В Р’В Р В РІР‚В Р В Р’В Р РЋРІР‚СћР В Р’В Р вЂ™Р’В·Р В Р’В Р В РІР‚В Р В Р Р‹Р В РІР‚С™Р В Р’В Р вЂ™Р’В°Р В Р Р‹Р Р†Р вЂљР’В°Р В Р’В Р вЂ™Р’В°Р В Р Р‹Р В РІР‚в„–Р В Р Р‹Р Р†Р вЂљРЎв„ў lower-Р В Р’В Р РЋРІР‚СњР В Р’В Р вЂ™Р’В»Р В Р Р‹Р В РІР‚в„–Р В Р Р‹Р Р†Р вЂљР Р‹Р В Р’В Р РЋРІР‚В Р В Р вЂ Р В РІР‚С™Р Р†Р вЂљРЎСљ transport Р В Р’В Р РЋР’ВР В Р’В Р вЂ™Р’В°Р В Р’В Р РЋРІР‚вЂќР В Р’В Р РЋРІР‚вЂќР В Р’В Р РЋРІР‚ВР В Р Р‹Р Р†Р вЂљРЎв„ў Р В Р’В Р В РІР‚В  Р В Р’В Р РЋРІР‚СњР В Р’В Р РЋРІР‚СћР В Р’В Р В РІР‚В¦Р В Р Р‹Р Р†Р вЂљРЎв„ўР В Р Р‹Р В РІР‚С™Р В Р’В Р вЂ™Р’В°Р В Р’В Р РЋРІР‚СњР В Р Р‹Р Р†Р вЂљРЎв„ў (camelCase Р В Р Р‹Р Р†Р вЂљР Р‹Р В Р’В Р вЂ™Р’ВµР В Р Р‹Р В РІР‚С™Р В Р’В Р вЂ™Р’ВµР В Р’В Р вЂ™Р’В· alias)
    return AttachmentDTO(
        id=data["id"],
        title=data.get("title"),
        original_filename=data["originalfilename"],
        content_type=data.get("contenttype"),
        size_bytes=data["sizebytes"],
        sha256=data.get("sha256"),
        storage_key=data.get("storagekey"),
        is_deleted=data.get("isdeleted", False),
        created_at=data["createdat"],
    )


@router.post("", response_model=AttachmentDTO)
async def upload_attachment(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    session: AsyncSession = Depends(get_db_session),
) -> AttachmentDTO:
    content = await file.read()

    repo = AttachmentRepository(session=session)
    uc = UploadAttachmentUseCase(repo=repo, storage=storage())

    data = await uc.execute(
        title=title,
        original_filename=file.filename or "file",
        content_type=file.content_type,
        content=content,
    )
    return _map_attachment_to_dto(data)


@router.get("", response_model=AttachmentListResponseDTO)
async def list_attachments(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session),
) -> AttachmentListResponseDTO:
    repo = AttachmentRepository(session=session)
    uc = ListAttachmentsUseCase(repo=repo)

    data = await uc.execute(limit=limit, offset=offset)

    return AttachmentListResponseDTO(
        items=[_map_attachment_to_dto(x) for x in data["items"]],
        limit=data["limit"],
        offset=data["offset"],
        total=data["total"],
    )


@router.get("/{attachmentId}", response_model=AttachmentDTO)
async def get_attachment(
    attachmentId: int,
    session: AsyncSession = Depends(get_db_session),
) -> AttachmentDTO:
    repo = AttachmentRepository(session=session)
    uc = GetAttachmentUseCase(repo=repo)

    data = await uc.execute(attachment_id=attachmentId)
    if data is None:
        raise HTTPException(status_code=404, detail="Not found")

    return _map_attachment_to_dto(data)


@router.delete("/{attachmentId}", response_model=GenericOkResponseDTO)
async def delete_attachment(
    attachmentId: int,
    session: AsyncSession = Depends(get_db_session),
) -> GenericOkResponseDTO:
    repo = AttachmentRepository(session=session)
    uc = DeleteAttachmentUseCase(repo=repo)

    try:
        await uc.execute(attachment_id=attachmentId)
    except ValueError as e:
        if str(e) == "notfound":
            raise HTTPException(status_code=404, detail="Not found")
        raise

    return GenericOkResponseDTO(success=True, message="Deleted")


@router.get("/{attachmentId}/download")
async def download_attachment(
    attachmentId: int,
    session: AsyncSession = Depends(get_db_session),
):
    repo = AttachmentRepository(session=session)
    uc = DownloadAttachmentUseCase(repo=repo, storage=storage())

    res = await uc.execute(attachment_id=attachmentId)
    if res is None:
        raise HTTPException(status_code=404, detail="Not found")

    meta, content = res

    filename = meta.get("originalfilename") or "file"
    contenttype = meta.get("contenttype") or "application/octet-stream"

    return StreamingResponse(
        iter([content]),
        media_type=contenttype,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
