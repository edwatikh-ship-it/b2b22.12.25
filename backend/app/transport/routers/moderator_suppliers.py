from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["ModeratorSuppliers"])


@router.get("/moderator/suppliers")
async def list_moderator_suppliers(q: str | None = None, limit: int = 50, offset: int = 0):
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.post("/moderator/suppliers")
async def create_moderator_supplier(payload: dict):
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.get("/moderator/suppliers/{supplierId}")
async def get_moderator_supplier(supplierId: int):
    raise HTTPException(status_code=501, detail="Not Implemented")


@router.put("/moderator/suppliers/{supplierId}")
async def update_moderator_supplier(supplierId: int, payload: dict):
    raise HTTPException(status_code=501, detail="Not Implemented")
