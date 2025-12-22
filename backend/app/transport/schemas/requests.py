from pydantic import BaseModel, Field


# SSoT: api-contracts.yaml
class RequestKeyInputDTO(BaseModel):
    pos: int = Field(..., ge=1)
    text: str = Field(..., min_length=1)
    qty: float | None = None
    unit: str | None = None


class CreateRequestManualRequestDTO(BaseModel):
    title: str | None = None
    keys: list[RequestKeyInputDTO]


class CreateRequestResponseDTO(BaseModel):
    success: bool
    requestid: int
    filename: str | None = None
    status: str
    message: str | None = None


class RequestSummaryDTO(BaseModel):
    id: int
    filename: str | None = None
    status: str
    createdat: str
    keyscount: int


class RequestListResponseDTO(BaseModel):
    items: list[RequestSummaryDTO]
    limit: int
    offset: int
    total: int


class RequestKeyDTO(BaseModel):
    id: int
    pos: int
    rawtext: str
    normalizedtext: str
    qty: float | None = None
    unit: str | None = None
    suppliers: list[dict]


class RequestDetailDTO(BaseModel):
    id: int
    filename: str | None = None
    status: str
    createdat: str
    keys: list[RequestKeyDTO]


class UpdateRequestKeysRequestDTO(BaseModel):
    keys: list[RequestKeyInputDTO]


class SubmitRequestResponseDTO(BaseModel):
    success: bool = True
    requestid: int
    newstatus: str
    matchedsuppliers: int
    message: str | None = None
