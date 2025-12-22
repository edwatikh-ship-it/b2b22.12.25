"""
Moderator suppliers router.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.session import get_db_session
from app.transport.schemas.moderator_suppliers import (
    CreateModeratorSupplierRequestDTO,
    ModeratorSupplierDTO,
    ModeratorSuppliersListResponseDTO,
    UpdateModeratorSupplierRequestDTO,
)
from app.usecases.create_moderator_supplier import create_moderator_supplier
from app.usecases.get_moderator_supplier import get_moderator_supplier
from app.usecases.list_moderator_suppliers import list_moderator_suppliers
from app.usecases.update_moderator_supplier import update_moderator_supplier

router = APIRouter(tags=["ModeratorSuppliers"])


@router.get("/moderator/suppliers", response_model=ModeratorSuppliersListResponseDTO)
async def list_moderator_suppliers_endpoint(
    q: Annotated[str | None, Query()] = None,
    type: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    sort: Annotated[str, Query()] = "name_asc",
    session: AsyncSession = Depends(get_db_session),
) -> ModeratorSuppliersListResponseDTO:
    return await list_moderator_suppliers(session, q, type, limit, offset, sort)


@router.post("/moderator/suppliers", response_model=ModeratorSupplierDTO)
async def create_moderator_supplier_endpoint(
    payload: CreateModeratorSupplierRequestDTO,
    session: AsyncSession = Depends(get_db_session),
) -> ModeratorSupplierDTO:
    return await create_moderator_supplier(session, payload)


@router.get("/moderator/suppliers/{supplierId}", response_model=ModeratorSupplierDTO)
async def get_moderator_supplier_endpoint(
    supplier_id: Annotated[int, Path(alias="supplierId")],
    session: AsyncSession = Depends(get_db_session),
) -> ModeratorSupplierDTO:
    try:
        return await get_moderator_supplier(session, supplier_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/moderator/suppliers/{supplierId}", response_model=ModeratorSupplierDTO)
async def update_moderator_supplier_endpoint(
    supplier_id: Annotated[int, Path(alias="supplierId")],
    payload: UpdateModeratorSupplierRequestDTO,
    session: AsyncSession = Depends(get_db_session),
) -> ModeratorSupplierDTO:
    try:
        return await update_moderator_supplier(session, supplier_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
