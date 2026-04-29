from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import hash_password, require_min_role
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.get("", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_min_role("admin")),
) -> List[UserResponse]:
    result = await db.execute(select(User).order_by(User.ad_account))
    return [UserResponse.model_validate(u) for u in result.scalars().all()]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_min_role("admin")),
) -> UserResponse:
    existing = await db.execute(select(User).where(User.ad_account == payload.ad_account))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="そのADアカウントは既に登録されています")
    data = payload.model_dump(exclude={"password"})
    user = User(**data)
    if payload.password:
        user.password_hash = hash_password(payload.password)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_min_role("admin")),
) -> UserResponse:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    data = payload.model_dump(exclude_unset=True, exclude={"password"})
    for k, v in data.items():
        setattr(user, k, v)
    if payload.password:
        user.password_hash = hash_password(payload.password)
    await db.flush()
    await db.refresh(user)
    return UserResponse.model_validate(user)
