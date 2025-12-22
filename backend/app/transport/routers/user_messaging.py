from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import RequestRepository
from app.adapters.db.session import get_db_session
from app.transport.schemas.user_messaging import (
    RecipientDTO,
    RecipientsResponseDTO,
    UpdateRecipientsRequestDTO,
)
from app.usecases.update_request_recipients import RecipientInput, UpdateRequestRecipientsUseCase

router = APIRouter(tags=["UserMessaging"])


@router.put("/user/requests/{requestId}/recipients", response_model=RecipientsResponseDTO)
async def update_recipients(
    requestId: int,
    payload: UpdateRecipientsRequestDTO,
    session: AsyncSession = Depends(get_db_session),
) -> RecipientsResponseDTO:
    repo = RequestRepository(session)
    uc = UpdateRequestRecipientsUseCase(repo)
    try:
        rows = await uc.execute(
            request_id=int(requestId),
            recipients=[
                RecipientInput(supplierid=r.supplierid, selected=r.selected)
                for r in payload.recipients
            ],
        )
    except ValueError as e:
        if str(e) == "not_found":
            raise HTTPException(status_code=404, detail="Not found")
        raise HTTPException(status_code=400, detail=str(e))

    return RecipientsResponseDTO(recipients=[RecipientDTO(**r) for r in rows])


@router.post("/user/requests/{requestId}/send")
async def send_request_messages(requestId: int, payload: dict):
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.post("/user/requests/{requestId}/send-new")
async def send_request_messages_new(requestId: int, payload: dict):
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get("/user/requests/{requestId}/messages")
async def list_request_messages(
    requestId: int, limit: int = 50, offset: int = 0, includedeleted: bool = False
):
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.delete("/user/messages/{messageId}")
async def delete_message(messageId: int):
    raise HTTPException(status_code=501, detail="Not Implemented")
