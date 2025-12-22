from pydantic import BaseModel, Field


class RecipientDTO(BaseModel):
    supplierid: int = Field(..., ge=1)
    selected: bool


class UpdateRecipientsRequestDTO(BaseModel):
    recipients: list[RecipientDTO]


class RecipientsResponseDTO(BaseModel):
    recipients: list[RecipientDTO]
