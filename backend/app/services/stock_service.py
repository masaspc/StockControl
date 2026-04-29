from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert_setting import AlertSetting
from app.models.item import Item
from app.models.stock import Stock


async def get_or_create_stock(
    db: AsyncSession, item_id: int, location_id: int
) -> Stock:
    result = await db.execute(
        select(Stock).where(Stock.item_id == item_id, Stock.location_id == location_id)
    )
    stock = result.scalar_one_or_none()
    if stock is None:
        stock = Stock(item_id=item_id, location_id=location_id, quantity=0)
        db.add(stock)
        await db.flush()
    return stock


async def adjust_quantity(
    db: AsyncSession, item_id: int, location_id: int, delta: int
) -> Stock:
    stock = await get_or_create_stock(db, item_id, location_id)
    new_qty = stock.quantity + delta
    if new_qty < 0:
        raise ValueError(
            f"在庫不足: item_id={item_id} location_id={location_id} "
            f"current={stock.quantity} delta={delta}"
        )
    stock.quantity = new_qty
    await db.flush()
    return stock


async def total_quantity_for_item(db: AsyncSession, item_id: int) -> int:
    result = await db.execute(
        select(func.coalesce(func.sum(Stock.quantity), 0)).where(Stock.item_id == item_id)
    )
    return int(result.scalar() or 0)


async def check_alert(
    db: AsyncSession, item_id: int
) -> Optional[tuple[Item, AlertSetting, int]]:
    """発注点割れの場合 (item, alert_setting, current_qty) を返す。"""
    item_result = await db.execute(select(Item).where(Item.id == item_id))
    item = item_result.scalar_one_or_none()
    if item is None or not item.is_active:
        return None

    alert_result = await db.execute(
        select(AlertSetting).where(
            AlertSetting.item_id == item_id, AlertSetting.is_active.is_(True)
        )
    )
    alert = alert_result.scalar_one_or_none()
    threshold = alert.order_point if alert else item.order_point
    if threshold <= 0:
        return None

    current_qty = await total_quantity_for_item(db, item_id)
    if current_qty <= threshold:
        return item, alert, current_qty
    return None
