from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_min_role
from app.models.serial_item import SerialItem
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.serial import SerialItemResponse, SerialItemUpdate
from app.schemas.transaction import TransactionResponse

router = APIRouter()


@router.get("", response_model=List[SerialItemResponse])
async def list_serials(
    item_id: Optional[int] = None,
    location_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("operator")),
) -> List[SerialItemResponse]:
    stmt = select(SerialItem)
    if item_id:
        stmt = stmt.where(SerialItem.item_id == item_id)
    if location_id:
        stmt = stmt.where(SerialItem.location_id == location_id)
    if status:
        stmt = stmt.where(SerialItem.status == status)
    stmt = stmt.order_by(SerialItem.serial_no)
    result = await db.execute(stmt)
    return [SerialItemResponse.model_validate(s) for s in result.scalars().all()]


@router.get("/search", response_model=List[SerialItemResponse])
async def search_serials(
    q: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("operator")),
) -> List[SerialItemResponse]:
    like = f"%{q}%"
    result = await db.execute(
        select(SerialItem).where(
            or_(SerialItem.serial_no.ilike(like), SerialItem.mac_address.ilike(like))
        )
    )
    return [SerialItemResponse.model_validate(s) for s in result.scalars().all()]


@router.get("/{serial_id}", response_model=SerialItemResponse)
async def get_serial(
    serial_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("operator")),
) -> SerialItemResponse:
    s = await db.get(SerialItem, serial_id)
    if not s:
        raise HTTPException(status_code=404, detail="シリアル品が見つかりません")
    return SerialItemResponse.model_validate(s)


@router.put("/{serial_id}", response_model=SerialItemResponse)
async def update_serial(
    serial_id: int,
    payload: SerialItemUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> SerialItemResponse:
    s = await db.get(SerialItem, serial_id)
    if not s:
        raise HTTPException(status_code=404, detail="シリアル品が見つかりません")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    await db.flush()
    await db.refresh(s)
    return SerialItemResponse.model_validate(s)


@router.get("/{serial_id}/history", response_model=List[TransactionResponse])
async def serial_history(
    serial_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("operator")),
) -> List[TransactionResponse]:
    result = await db.execute(
        select(Transaction)
        .where(Transaction.serial_item_id == serial_id)
        .order_by(Transaction.created_at.desc())
    )
    return [TransactionResponse.model_validate(t) for t in result.scalars().all()]
