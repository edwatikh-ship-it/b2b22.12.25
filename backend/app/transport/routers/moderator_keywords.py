"""
Moderator keywords base router.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.session import get_db_session
from app.transport.schemas.moderator_keywords import KeywordsListResponseDTO
from app.usecases.list_keywords import list_keywords

router = APIRouter(tags=["ModeratorKeywords"])


@router.get("/moderator/keywords", response_model=KeywordsListResponseDTO)
async def list_keywords_endpoint(
    q: Annotated[str | None, Query()] = None,
    status: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    sort: Annotated[str, Query()] = "keyword_asc",
    session: AsyncSession = Depends(get_db_session),
) -> KeywordsListResponseDTO:
    return await list_keywords(session, q, status, limit, offset, sort)
