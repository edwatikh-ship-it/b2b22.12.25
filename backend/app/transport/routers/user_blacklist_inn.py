from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import UserBlacklistInnRepository
from app.adapters.db.session import get_db_session
from app.transport.schemas.blacklist import (
    AddUserBlacklistInnRequestDTO,
    UserBlacklistInnItemDTO,
    UserBlacklistInnListResponseDTO,
)
from app.usecases.add_user_blacklist_inn import AddUserBlacklistInnUseCase
from app.usecases.list_user_blacklist_inn import ListUserBlacklistInnUseCase
from app.usecases.remove_user_blacklist_inn import RemoveUserBlacklistInnUseCase

router = APIRouter(tags=["UserBlacklist"])


def _require_user_id(authorization: str | None) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    return 1


@router.post("/user/blacklist-inn")
async def add_user_blacklist_inn(
    payload: AddUserBlacklistInnRequestDTO,
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db_session),
):
    user_id = _require_user_id(authorization)
    repo = UserBlacklistInnRepository(db)
    await AddUserBlacklistInnUseCase(repo).execute(
        user_id=user_id, inn=payload.inn, reason=payload.reason
    )
    return {"success": True}


@router.get("/user/blacklist-inn", response_model=UserBlacklistInnListResponseDTO)
async def list_user_blacklist_inn(
    limit: int = 200,
    offset: int = 0,
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db_session),
):
    user_id = _require_user_id(authorization)
    repo = UserBlacklistInnRepository(db)

    # Usecase currently returns items only; transport shapes response to SSoT
    raw_items = await ListUserBlacklistInnUseCase(repo).execute(user_id=user_id, limit=limit)

    items = [UserBlacklistInnItemDTO(**x) for x in (raw_items or [])]
    total = len(items)

    return {"items": items, "limit": limit, "offset": offset, "total": total}


@router.delete("/user/blacklist-inn/{inn}")
async def remove_user_blacklist_inn(
    inn: str,
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db_session),
):
    user_id = _require_user_id(authorization)
    repo = UserBlacklistInnRepository(db)
    await RemoveUserBlacklistInnUseCase(repo).execute(user_id=user_id, inn=inn)
    return {"success": True}
