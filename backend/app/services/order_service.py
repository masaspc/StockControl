from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order


async def generate_order_no(db: AsyncSession) -> str:
    """PO-YYMM-NNN 形式で次の発注番号を採番"""
    now = datetime.now(timezone.utc)
    prefix = f"PO-{now:%y%m}-"
    result = await db.execute(
        select(func.count(Order.id)).where(Order.order_no.like(f"{prefix}%"))
    )
    count = int(result.scalar() or 0)
    return f"{prefix}{count + 1:03d}"
