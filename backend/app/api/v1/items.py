from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_min_role
from app.models.item import Item
from app.models.user import User
from app.schemas.common import Message
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate

router = APIRouter()


@router.get("", response_model=List[ItemResponse])
async def list_items(
    q: Optional[str] = None,
    category: Optional[str] = None,
    active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("viewer")),
) -> List[ItemResponse]:
    stmt = select(Item)
    if active is not None:
        stmt = stmt.where(Item.is_active == active)
    if category:
        stmt = stmt.where(Item.category == category)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(Item.code.ilike(like), Item.name.ilike(like), Item.barcode.ilike(like))
        )
    stmt = stmt.order_by(Item.code)
    result = await db.execute(stmt)
    return [ItemResponse.model_validate(r) for r in result.scalars().all()]


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: ItemCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> ItemResponse:
    existing = await db.execute(select(Item).where(Item.code == payload.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"品目コード '{payload.code}' は既に存在します")
    item = Item(**payload.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return ItemResponse.model_validate(item)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("viewer")),
) -> ItemResponse:
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="品目が見つかりません")
    return ItemResponse.model_validate(item)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    payload: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> ItemResponse:
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="品目が見つかりません")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    await db.flush()
    await db.refresh(item)
    return ItemResponse.model_validate(item)


@router.delete("/{item_id}", response_model=Message)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> Message:
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="品目が見つかりません")
    item.is_active = False
    await db.flush()
    return Message(message="品目を無効化しました")
