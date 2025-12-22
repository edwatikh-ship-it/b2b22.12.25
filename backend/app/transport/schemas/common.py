from __future__ import annotations

from pydantic import BaseModel


class GenericOkResponseDTO(BaseModel):
    success: bool
    message: str | None = None
