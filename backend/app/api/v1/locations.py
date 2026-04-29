from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_min_role
from app.models.location import Location
from app.models.user import User
from app.schemas.common import Message
from app.schemas.location import (
    LocationCreate,
    LocationResponse,
    LocationTreeNode,
    LocationUpdate,
)

router = APIRouter()


@router.get("", response_model=List[LocationTreeNode])
async def list_locations(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("viewer")),
) -> List[LocationTreeNode]:
    result = await db.execute(select(Location).where(Location.is_active.is_(True)).order_by(Location.code))
    locs = result.scalars().all()
    nodes: Dict[int, LocationTreeNode] = {
        loc.id: LocationTreeNode.model_validate(loc) for loc in locs
    }
    roots: List[LocationTreeNode] = []
    for loc in locs:
        node = nodes[loc.id]
        if loc.parent_id and loc.parent_id in nodes:
            nodes[loc.parent_id].children.append(node)
        else:
            roots.append(node)
    return roots


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    payload: LocationCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("admin")),
) -> LocationResponse:
    existing = await db.execute(select(Location).where(Location.code == payload.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"ロケーションコード '{payload.code}' は既に存在します")
    loc = Location(**payload.model_dump())
    db.add(loc)
    await db.flush()
    await db.refresh(loc)
    return LocationResponse.model_validate(loc)


@router.get("/{loc_id}", response_model=LocationResponse)
async def get_location(
    loc_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("viewer")),
) -> LocationResponse:
    loc = await db.get(Location, loc_id)
    if not loc:
        raise HTTPException(status_code=404, detail="ロケーションが見つかりません")
    return LocationResponse.model_validate(loc)


@router.put("/{loc_id}", response_model=LocationResponse)
async def update_location(
    loc_id: int,
    payload: LocationUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("admin")),
) -> LocationResponse:
    loc = await db.get(Location, loc_id)
    if not loc:
        raise HTTPException(status_code=404, detail="ロケーションが見つかりません")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(loc, k, v)
    await db.flush()
    await db.refresh(loc)
    return LocationResponse.model_validate(loc)


@router.delete("/{loc_id}", response_model=Message)
async def delete_location(
    loc_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("admin")),
) -> Message:
    loc = await db.get(Location, loc_id)
    if not loc:
        raise HTTPException(status_code=404, detail="ロケーションが見つかりません")
    loc.is_active = False
    await db.flush()
    return Message(message="ロケーションを無効化しました")
