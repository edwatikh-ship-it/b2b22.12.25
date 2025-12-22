from pydantic import BaseModel, Field


class SupplierSearchItemDTO(BaseModel):
    supplierid: int = Field(..., ge=1)
    suppliername: str = Field(..., min_length=1)
    inn: str = Field(..., min_length=10, max_length=12)
    website: str | None = None
    email: str | None = None
    score: float | None = None


class SuppliersSearchResponseDTO(BaseModel):
    items: list[SupplierSearchItemDTO]
    limit: int = Field(..., ge=1, le=200)
