from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_min_role
from app.models.item import Item
from app.models.location import Location
from app.models.serial_item import SerialItem
from app.models.stock import Stock
from app.models.user import User
from app.schemas.stock import StockDetailResponse, StockSummary

router = APIRouter()


@router.get("", response_model=List[StockDetailResponse])
async def list_stocks(
    item_id: Optional[int] = None,
    location_id: Optional[int] = None,
    alert: bool = False,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("viewer")),
) -> List[StockDetailResponse]:
    stmt = (
        select(
            Stock.id,
            Stock.item_id,
            Stock.location_id,
            Stock.quantity,
            Stock.updated_at,
            Item.code.label("item_code"),
            Item.name.label("item_name"),
            Item.order_point,
            Location.code.label("location_code"),
            Location.name.label("location_name"),
        )
        .join(Item, Item.id == Stock.item_id)
        .join(Location, Location.id == Stock.location_id)
    )
    if item_id:
        stmt = stmt.where(Stock.item_id == item_id)
    if location_id:
        stmt = stmt.where(Stock.location_id == location_id)
    result = await db.execute(stmt)
    rows = result.all()
    out: List[StockDetailResponse] = []
    for r in rows:
        m = r._mapping
        is_alert = m["order_point"] is not None and m["quantity"] <= m["order_point"]
        if alert and not is_alert:
            continue
        out.append(
            StockDetailResponse(
                id=m["id"],
                item_id=m["item_id"],
                location_id=m["location_id"],
                quantity=m["quantity"],
                updated_at=m["updated_at"],
                item_code=m["item_code"],
                item_name=m["item_name"],
                location_code=m["location_code"],
                location_name=m["location_name"],
                order_point=m["order_point"],
                is_alert=is_alert,
            )
        )
    return out


@router.get("/summary", response_model=StockSummary)
async def stocks_summary(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("viewer")),
) -> StockSummary:
    items_count = (await db.execute(select(func.count(Item.id)).where(Item.is_active.is_(True)))).scalar() or 0
    loc_count = (await db.execute(select(func.count(Location.id)).where(Location.is_active.is_(True)))).scalar() or 0

    # アラート集計（item単位の総在庫が発注点以下）
    item_qty_subq = (
        select(Stock.item_id, func.coalesce(func.sum(Stock.quantity), 0).label("total"))
        .group_by(Stock.item_id)
        .subquery()
    )
    alert_count = (
        await db.execute(
            select(func.count())
            .select_from(Item)
            .outerjoin(item_qty_subq, item_qty_subq.c.item_id == Item.id)
            .where(
                Item.is_active.is_(True),
                Item.order_point > 0,
                func.coalesce(item_qty_subq.c.total, 0) <= Item.order_point,
            )
        )
    ).scalar() or 0

    serial_total = (await db.execute(select(func.count(SerialItem.id)))).scalar() or 0
    serial_in = (
        await db.execute(select(func.count(SerialItem.id)).where(SerialItem.status == "in_stock"))
    ).scalar() or 0
    serial_out = (
        await db.execute(select(func.count(SerialItem.id)).where(SerialItem.status == "checked_out"))
    ).scalar() or 0

    return StockSummary(
        total_items=int(items_count),
        total_locations=int(loc_count),
        alert_items=int(alert_count),
        serial_items_total=int(serial_total),
        serial_items_in_stock=int(serial_in),
        serial_items_checked_out=int(serial_out),
    )


@router.get("/alerts", response_model=List[StockDetailResponse])
async def stocks_alerts(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("viewer")),
) -> List[StockDetailResponse]:
    return await list_stocks(alert=True, db=db, _user=_user)
