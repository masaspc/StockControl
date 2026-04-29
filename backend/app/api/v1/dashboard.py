from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_min_role
from app.models.item import Item
from app.models.location import Location
from app.models.order import Order
from app.models.serial_item import SerialItem
from app.models.stock import Stock
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.dashboard import AlertItem, DashboardResponse, RecentTransaction

router = APIRouter()


@router.get("", response_model=DashboardResponse)
async def dashboard(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("viewer")),
) -> DashboardResponse:
    # KPI
    total_items = (
        await db.execute(select(func.count(Item.id)).where(Item.is_active.is_(True)))
    ).scalar() or 0

    total_locations = (
        await db.execute(select(func.count(Location.id)).where(Location.is_active.is_(True)))
    ).scalar() or 0

    total_serials = (
        await db.execute(select(func.count(SerialItem.id)))
    ).scalar() or 0

    pending_orders = (
        await db.execute(
            select(func.count(Order.id)).where(Order.status.in_(["draft", "pending", "approved"]))
        )
    ).scalar() or 0

    # 今日の入出庫
    today = datetime.now(timezone.utc).date()
    today_start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)

    today_in = (
        await db.execute(
            select(func.coalesce(func.sum(Transaction.quantity), 0)).where(
                Transaction.tx_type == "in",
                Transaction.created_at >= today_start,
            )
        )
    ).scalar() or 0

    today_out = (
        await db.execute(
            select(func.coalesce(func.sum(Transaction.quantity), 0)).where(
                Transaction.tx_type == "out",
                Transaction.created_at >= today_start,
            )
        )
    ).scalar() or 0

    # アラート品目
    item_qty_subq = (
        select(Stock.item_id, func.coalesce(func.sum(Stock.quantity), 0).label("total"))
        .group_by(Stock.item_id)
        .subquery()
    )
    alert_rows = await db.execute(
        select(
            Item.id,
            Item.code,
            Item.name,
            Item.unit,
            Item.order_point,
            func.coalesce(item_qty_subq.c.total, 0).label("qty"),
        )
        .outerjoin(item_qty_subq, item_qty_subq.c.item_id == Item.id)
        .where(
            Item.is_active.is_(True),
            Item.order_point > 0,
            func.coalesce(item_qty_subq.c.total, 0) <= Item.order_point,
        )
        .limit(10)
    )
    alerts = [
        AlertItem(
            item_id=r.id,
            item_code=r.code,
            item_name=r.name,
            current_qty=int(r.qty),
            order_point=r.order_point,
            unit=r.unit,
        )
        for r in alert_rows.all()
    ]

    # 最新トランザクション
    recent_rows = await db.execute(
        select(Transaction, Item.name.label("item_name"), User.display_name.label("op_name"))
        .join(Item, Item.id == Transaction.item_id)
        .outerjoin(User, User.id == Transaction.operator_id)
        .order_by(Transaction.created_at.desc())
        .limit(10)
    )
    recent: list[RecentTransaction] = []
    for row in recent_rows.all():
        tx = row[0]
        recent.append(
            RecentTransaction(
                id=tx.id,
                tx_type=tx.tx_type,
                item_name=row.item_name,
                quantity=tx.quantity,
                operator_name=row.op_name,
                created_at=tx.created_at,
            )
        )

    return DashboardResponse(
        total_items=int(total_items),
        total_locations=int(total_locations),
        total_serials=int(total_serials),
        alert_count=len(alerts),
        pending_orders=int(pending_orders),
        today_in=int(today_in),
        today_out=int(today_out),
        alerts=alerts,
        recent_transactions=recent,
    )
