from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.services.stock_service import check_alert
from app.utils.email import render_alert_text, send_email

logger = logging.getLogger(__name__)


async def check_and_notify(item_id: int) -> None:
    """発注点アラートを判定して通知。BackgroundTasksで呼び出される想定。"""
    async with AsyncSessionLocal() as db:  # type: AsyncSession
        try:
            result = await check_alert(db, item_id)
            if result is None:
                return
            item, alert, current_qty = result
            if alert is None or not alert.notify_to:
                logger.info("No alert recipients for item_id=%s", item_id)
                return

            subject = f"【在庫アラート】{item.name} の在庫が発注点を下回りました"
            body = render_alert_text(
                item_name=item.name,
                item_code=item.code,
                current_qty=current_qty,
                order_point=alert.order_point,
                unit=item.unit,
            )
            sent = await send_email(alert.notify_to, subject, body)
            if sent:
                alert.last_notified_at = datetime.now(timezone.utc)
                await db.commit()
        except Exception:
            logger.exception("Alert notification failed for item_id=%s", item_id)
