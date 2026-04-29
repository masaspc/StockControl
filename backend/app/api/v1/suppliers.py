from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_min_role
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.supplier import SupplierCreate, SupplierResponse

router = APIRouter()


@router.get("", response_model=List[SupplierResponse])
async def list_suppliers(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> List[SupplierResponse]:
    result = await db.execute(
        select(Supplier).where(Supplier.is_active.is_(True)).order_by(Supplier.name)
    )
    return [SupplierResponse.model_validate(s) for s in result.scalars().all()]


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    payload: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> SupplierResponse:
    supplier = Supplier(**payload.model_dump())
    db.add(supplier)
    await db.flush()
    await db.refresh(supplier)
    return SupplierResponse.model_validate(supplier)
