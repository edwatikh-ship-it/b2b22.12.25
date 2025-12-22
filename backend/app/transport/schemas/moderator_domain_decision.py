from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, HttpUrl

from app.transport.schemas.supplier_cards import SupplierCardDTO


class DomainDecisionStatus(str, Enum):
    supplier = "supplier"
    reseller = "reseller"
    blacklist = "blacklist"
    pending = "pending"


class DomainDecisionCardDataDTO(BaseModel):
    inn: Annotated[str, Field(min_length=10, max_length=12)]
    name: Annotated[str, Field(min_length=1, max_length=500)]
    email: EmailStr
    emails: Annotated[list[EmailStr] | None, Field(max_length=10)] = None
    phone: str | None = None
    comment: Annotated[str | None, Field(max_length=2000)] = None

    model_config = {"extra": "forbid"}


class DomainDecisionRequestDTO(BaseModel):
    status: DomainDecisionStatus
    carddata: DomainDecisionCardDataDTO | None = None
    comment: Annotated[str | None, Field(max_length=2000)] = None

    model_config = {"extra": "forbid"}


# Reuse existing SupplierCardDTO schema from moderator_suppliers module.
# This keeps a single source of Python truth for that DTO in code.
class DomainDecisionResponseDTO(BaseModel):
    domain: str
    status: DomainDecisionStatus
    decisionat: str
    supplierid: int | None = None
    card: SupplierCardDTO | None = None
    comment: str | None = None
    urls: list[HttpUrl]

    model_config = {"extra": "forbid"}
