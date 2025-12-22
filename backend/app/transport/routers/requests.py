from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import RequestRepository
from app.adapters.db.session import get_db_session
from app.transport.schemas.requests import (
    CreateRequestManualRequestDTO,
    CreateRequestResponseDTO,
    RequestDetailDTO,
    RequestKeyDTO,
    RequestListResponseDTO,
    RequestSummaryDTO,
    SubmitRequestResponseDTO,
    UpdateRequestKeysRequestDTO,
)
from app.usecases.create_request_manual import CreateRequestManualUseCase
from app.usecases.create_request_manual import KeyInput as CreateKeyInput
from app.usecases.submit_request import SubmitRequestUseCase
from app.usecases.update_request_keys import KeyInput as UpdateKeyInput
from app.usecases.update_request_keys import UpdateRequestKeysUseCase

router = APIRouter(prefix="/user/requests", tags=["UserRequests"])


@router.post("", response_model=CreateRequestResponseDTO)
async def create_request_manual(
    payload: CreateRequestManualRequestDTO,
    session: AsyncSession = Depends(get_db_session),
) -> CreateRequestResponseDTO:
    try:
        repo = RequestRepository(session)
        uc = CreateRequestManualUseCase(repo)
        request_id = await uc.execute(
            title=payload.title,
            keys=[
                CreateKeyInput(pos=k.pos, text=k.text, qty=k.qty, unit=k.unit) for k in payload.keys
            ],
        )
        return CreateRequestResponseDTO(
            success=True,
            requestid=request_id,
            filename=None,
            status="draft",
            message=None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=RequestListResponseDTO)
async def list_user_requests(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> RequestListResponseDTO:
    repo = RequestRepository(session)
    data = await repo.list_requests(limit=limit, offset=offset)

    items = [
        RequestSummaryDTO(
            id=i["id"],
            filename=i["filename"],
            status=i["status"],
            createdat=i["createdat"],
            keyscount=i["keyscount"],
        )
        for i in data["items"]
    ]
    return RequestListResponseDTO(items=items, limit=limit, offset=offset, total=data["total"])


@router.get("/{requestId}", response_model=RequestDetailDTO)
async def get_user_request_detail(
    requestId: int,
    session: AsyncSession = Depends(get_db_session),
) -> RequestDetailDTO:
    repo = RequestRepository(session)
    data = await repo.get_detail(request_id=requestId)
    if data is None:
        raise HTTPException(status_code=404, detail="Not found")

    return RequestDetailDTO(
        id=data["id"],
        filename=data["filename"],
        status=data["status"],
        createdat=data["createdat"],
        keys=[RequestKeyDTO(**k) for k in data["keys"]],
    )


@router.put("/{requestId}/keys", response_model=RequestDetailDTO)
async def update_user_request_keys(
    requestId: int,
    payload: UpdateRequestKeysRequestDTO,
    session: AsyncSession = Depends(get_db_session),
) -> RequestDetailDTO:
    repo = RequestRepository(session)
    uc = UpdateRequestKeysUseCase(repo)
    try:
        await uc.execute(
            request_id=requestId,
            keys=[
                UpdateKeyInput(pos=k.pos, text=k.text, qty=k.qty, unit=k.unit) for k in payload.keys
            ],
        )
    except ValueError as e:
        if str(e) == "not_found":
            raise HTTPException(status_code=404, detail="Not found")
        raise HTTPException(status_code=400, detail=str(e))

    data = await repo.get_detail(request_id=requestId)
    if data is None:
        raise HTTPException(status_code=404, detail="Not found")

    return RequestDetailDTO(
        id=data["id"],
        filename=data["filename"],
        status=data["status"],
        createdat=data["createdat"],
        keys=[RequestKeyDTO(**k) for k in data["keys"]],
    )


@router.post("/{requestId}/submit", response_model=SubmitRequestResponseDTO)
async def submit_user_request(
    requestId: int,
    session: AsyncSession = Depends(get_db_session),
) -> SubmitRequestResponseDTO:
    repo = RequestRepository(session)
    uc = SubmitRequestUseCase(repo)
    try:
        data = await uc.execute(request_id=requestId)
    except ValueError as e:
        if str(e) == "not_found":
            raise HTTPException(status_code=404, detail="Not found")
        if str(e) == "invalid_state":
            raise HTTPException(status_code=400, detail="Invalid state")
        raise HTTPException(status_code=400, detail=str(e))

    return SubmitRequestResponseDTO(
        success=True,
        requestid=data["requestid"],
        newstatus=data["newstatus"],
        matchedsuppliers=int(data["matchedsuppliers"]),
        message=data["message"],
    )
