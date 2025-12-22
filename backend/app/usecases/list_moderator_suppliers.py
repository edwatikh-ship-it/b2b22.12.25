"""
List moderator suppliers usecase - real DB implementation.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import ModeratorSupplierRepository
from app.transport.schemas.moderator_suppliers import (
    ModeratorSupplierDTO,
    ModeratorSuppliersListResponseDTO,
)


async def list_moderator_suppliers(
    session: AsyncSession,
    q: str | None = None,
    type_filter: str | None = None,
    limit: int = 50,
    offset: int = 0,
    sort: str = "name_asc",
) -> ModeratorSuppliersListResponseDTO:
    """
    List moderator suppliers from real DB.
    """
    repo = ModeratorSupplierRepository(session)
    items, total = await repo.list_suppliers(q, type_filter, limit, offset, sort)

    return ModeratorSuppliersListResponseDTO(
        items=[
            ModeratorSupplierDTO(
                id=s.id,
                name=s.name,
                inn=s.inn,
                email=s.email,
                domain=s.domain,
                type=s.type,
                createdAt=s.created_at,
                updatedAt=s.updated_at,
            )
            for s in items
        ],
        limit=limit,
        offset=offset,
        total=total,
    )
