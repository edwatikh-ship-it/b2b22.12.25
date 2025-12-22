"""
Update moderator supplier usecase - real DB implementation.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import ModeratorSupplierRepository
from app.transport.schemas.moderator_suppliers import (
    ModeratorSupplierDTO,
    UpdateModeratorSupplierRequestDTO,
)


async def update_moderator_supplier(
    session: AsyncSession,
    supplier_id: int,
    dto: UpdateModeratorSupplierRequestDTO,
) -> ModeratorSupplierDTO:
    """
    Update a moderator supplier in DB.
    """
    repo = ModeratorSupplierRepository(session)

    # Build updates dict with only non-None values
    updates = {}
    if dto.name is not None:
        updates["name"] = dto.name
    if dto.inn is not None:
        updates["inn"] = dto.inn
    if dto.email is not None:
        updates["email"] = dto.email
    if dto.domain is not None:
        updates["domain"] = dto.domain
    if dto.type is not None:
        updates["type"] = dto.type

    supplier = await repo.update_supplier(supplier_id, updates)

    if not supplier:
        raise ValueError(f"Supplier {supplier_id} not found")

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
