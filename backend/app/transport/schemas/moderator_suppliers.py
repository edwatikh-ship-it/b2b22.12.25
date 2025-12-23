"""
Schemas for moderator suppliers base.
SSoT: api-contracts.yaml
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SupplierType(str, Enum):
    """Supplier type."""
    supplier = "supplier"
    reseller = "reseller"


class ModeratorSupplierDTO(BaseModel):
    """Moderator supplier DTO."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    inn: str | None = None
    email: EmailStr | None = None
    domain: str | None = None
    type: SupplierType
    createdAt: datetime
    updatedAt: datetime


class CreateModeratorSupplierRequestDTO(BaseModel):
    """Request to create a moderator supplier."""
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1)
    inn: str = Field(..., min_length=10, max_length=12)
    email: EmailStr = Field(...)
    domain: str | None = None
    type: SupplierType = SupplierType.supplier


class UpdateModeratorSupplierRequestDTO(BaseModel):
    """Request to update a moderator supplier."""
    model_config = ConfigDict(from_attributes=True)

    name: str | None = None
    inn: str | None = None
    email: EmailStr | None = None
    domain: str | None = None
    type: SupplierType | None = None


class ModeratorSuppliersListResponseDTO(BaseModel):
    """Response with list of moderator suppliers."""
    model_config = ConfigDict(from_attributes=True)

    items: list[ModeratorSupplierDTO]
    limit: int
    offset: int
    total: int
