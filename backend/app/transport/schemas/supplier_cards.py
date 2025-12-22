from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, HttpUrl


class SupplierCardType(str, Enum):
    supplier = "supplier"
    reseller = "reseller"


class SupplierCardDTO(BaseModel):
    supplierid: int
    type: SupplierCardType
    inn: str
    name: str
    email: EmailStr
    emails: list[EmailStr] | None = None
    phone: str | None = None
    urls: list[HttpUrl]
    comment: str | None = None
    createdat: str
    updatedat: str
    checko: dict[str, Any] | None = None

    model_config = {"extra": "forbid"}
