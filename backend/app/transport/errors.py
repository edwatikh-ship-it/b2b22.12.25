from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: dict[str, Any] | None = None
