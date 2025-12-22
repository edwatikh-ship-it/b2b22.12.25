"""
Create moderator supplier usecase - real DB implementation.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import ModeratorSupplierRepository
from app.transport.schemas.moderator_suppliers import (
    CreateModeratorSupplierRequestDTO,
    ModeratorSupplierDTO,
)


async def create_moderator_supplier(
    session: AsyncSession,
    dto: CreateModeratorSupplierRequestDTO,
) -> ModeratorSupplierDTO:
    """
    Create a new moderator supplier in DB.
    """
    repo = ModeratorSupplierRepository(session)
    supplier = await repo.create_supplier(
        name=dto.name,
        inn=dto.inn,
        email=dto.email,
        domain=dto.domain,
        type_=dto.type,
    )
    
    return ModeratorSupplierDTO(
        id=supplier.id,
        name=supplier.name,
        inn=supplier.inn,
        email=supplier.email,
        domain=supplier.domain,
        type=supplier.type,
        createdAt=supplier.created_at,
        updatedAt=supplier.updated_at,
    )
