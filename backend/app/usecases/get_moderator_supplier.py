"""
Get moderator supplier usecase - real DB implementation.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import ModeratorSupplierRepository
from app.transport.schemas.moderator_suppliers import ModeratorSupplierDTO


async def get_moderator_supplier(
    session: AsyncSession,
    supplier_id: int,
) -> ModeratorSupplierDTO:
    """
    Get a moderator supplier by ID from DB.
    """
    repo = ModeratorSupplierRepository(session)
    supplier = await repo.get_supplier_by_id(supplier_id)

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
