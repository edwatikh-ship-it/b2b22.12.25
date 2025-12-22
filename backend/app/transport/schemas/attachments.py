from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AttachmentDTO(BaseModel):
    """
    SSoT: api-contracts.yaml /components/schemas/Attachment

    ВАЖНО:
    - наружу отдаём lower-without-separators: originalfilename, contenttype, sizebytes, storagekey, isdeleted, createdat
    - внутри держим snake_case: original_filename, content_type, size_bytes, storage_key, is_deleted, created_at
    """

    model_config = ConfigDict(
        populate_by_name=True,
        # КРИТИЧНО: не используем camelCase alias и не включаем серилизацию по alias глобально.
        # Мы управляем alias вручную, строго по api-contracts.yaml.
        ser_json_by_alias=True,
        extra="forbid",
    )

    id: int
    title: str | None = None

    original_filename: str = Field(..., alias="originalfilename")
    content_type: str | None = Field(default=None, alias="contenttype")
    size_bytes: int = Field(..., alias="sizebytes")

    sha256: str | None = None
    storage_key: str | None = Field(default=None, alias="storagekey")

    is_deleted: bool = Field(default=False, alias="isdeleted")
    created_at: str = Field(..., alias="createdat")


class AttachmentListResponseDTO(BaseModel):
    """
    SSoT: api-contracts.yaml /components/schemas/AttachmentListResponse
    """

    model_config = ConfigDict(
        populate_by_name=True,
        ser_json_by_alias=True,
        extra="forbid",
    )

    items: list[AttachmentDTO]
    limit: int
    offset: int
    total: int


class GenericOkResponseDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool = True
    message: str | None = None
