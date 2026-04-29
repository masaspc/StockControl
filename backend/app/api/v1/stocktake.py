from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_min_role
from app.models.item import Item
from app.models.location import Location
from app.models.stock import Stock
from app.models.stocktake import StocktakeRecord, StocktakeSession
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.common import Message
from app.schemas.stocktake import (
    StocktakeCreate,
    StocktakeDiff,
    StocktakeScan,
    StocktakeSessionResponse,
)
from app.services.stock_service import adjust_quantity

router = APIRouter()


@router.get("", response_model=List[StocktakeSessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> List[StocktakeSessionResponse]:
    result = await db.execute(select(StocktakeSession).order_by(StocktakeSession.started_at.desc()))
    return [StocktakeSessionResponse.model_validate(s) for s in result.scalars().all()]


@router.post("", response_model=StocktakeSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: StocktakeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_min_role("manager")),
) -> StocktakeSessionResponse:
    s = StocktakeSession(
        name=payload.name,
        location_id=payload.location_id,
        note=payload.note,
        started_by=user.id,
        status="open",
    )
    db.add(s)
    await db.flush()
    await db.refresh(s)
    return StocktakeSessionResponse.model_validate(s)


@router.post("/{session_id}/scan", response_model=Message)
async def scan(
    session_id: int,
    payload: StocktakeScan,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> Message:
    session = await db.get(StocktakeSession, session_id)
    if not session or session.status != "open":
        raise HTTPException(status_code=400, detail="開始中の棚卸セッションではありません")
    # 既存レコード upsert
    existing = await db.execute(
        select(StocktakeRecord).where(
            StocktakeRecord.session_id == session_id,
            StocktakeRecord.item_id == payload.item_id,
            StocktakeRecord.location_id == payload.location_id,
        )
    )
    rec = existing.scalar_one_or_none()
    # 期待値（現在の在庫数）
    stock_q = await db.execute(
        select(Stock.quantity).where(
            Stock.item_id == payload.item_id, Stock.location_id == payload.location_id
        )
    )
    expected = stock_q.scalar() or 0
    if rec:
        rec.counted_qty = payload.counted_qty
        rec.expected_qty = expected
        rec.note = payload.note
    else:
        rec = StocktakeRecord(
            session_id=session_id,
            item_id=payload.item_id,
            location_id=payload.location_id,
            expected_qty=expected,
            counted_qty=payload.counted_qty,
            note=payload.note,
        )
        db.add(rec)
    await db.flush()
    return Message(message="記録しました")


@router.get("/{session_id}/diff", response_model=List[StocktakeDiff])
async def diff(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> List[StocktakeDiff]:
    result = await db.execute(
        select(
            StocktakeRecord.item_id,
            StocktakeRecord.location_id,
            StocktakeRecord.expected_qty,
            StocktakeRecord.counted_qty,
            Item.code.label("item_code"),
            Item.name.label("item_name"),
            Location.name.label("location_name"),
        )
        .join(Item, Item.id == StocktakeRecord.item_id)
        .join(Location, Location.id == StocktakeRecord.location_id)
        .where(StocktakeRecord.session_id == session_id)
    )
    out = []
    for r in result.all():
        m = r._mapping
        out.append(
            StocktakeDiff(
                item_id=m["item_id"],
                item_code=m["item_code"],
                item_name=m["item_name"],
                location_id=m["location_id"],
                location_name=m["location_name"],
                expected_qty=m["expected_qty"],
                counted_qty=m["counted_qty"],
                diff=m["counted_qty"] - m["expected_qty"],
            )
        )
    return out


@router.post("/{session_id}/adjust", response_model=Message)
async def adjust(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_min_role("manager")),
) -> Message:
    session = await db.get(StocktakeSession, session_id)
    if not session or session.status != "open":
        raise HTTPException(status_code=400, detail="開始中の棚卸セッションではありません")
    result = await db.execute(
        select(StocktakeRecord).where(StocktakeRecord.session_id == session_id)
    )
    for rec in result.scalars().all():
        delta = rec.counted_qty - rec.expected_qty
        if delta == 0:
            continue
        await adjust_quantity(db, rec.item_id, rec.location_id, delta)
        db.add(
            Transaction(
                tx_type="adjust",
                item_id=rec.item_id,
                quantity=abs(delta),
                from_location_id=rec.location_id if delta < 0 else None,
                to_location_id=rec.location_id if delta > 0 else None,
                operator_id=user.id,
                note=f"棚卸調整 (session={session_id})",
            )
        )
    session.status = "closed"
    session.closed_at = datetime.now(timezone.utc)
    await db.flush()
    return Message(message="差異を調整して棚卸を確定しました")
