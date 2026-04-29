from __future__ import annotations

import logging
from email.message import EmailMessage
from typing import Iterable

import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(
    to: Iterable[str],
    subject: str,
    body_text: str,
    body_html: str | None = None,
) -> bool:
    if not settings.SMTP_ENABLED:
        logger.info("SMTP disabled. Would send to=%s subject=%s", list(to), subject)
        return False

    recipients = list(to)
    if not recipients:
        logger.warning("No recipients for email subject=%s", subject)
        return False

    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content(body_text)
    if body_html:
        msg.add_alternative(body_html, subtype="html")

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER or None,
            password=settings.SMTP_PASSWORD or None,
            start_tls=settings.SMTP_USE_TLS,
        )
        return True
    except Exception:
        logger.exception("Failed to send email")
        return False


def render_alert_text(
    item_name: str, item_code: str, current_qty: int, order_point: int, unit: str
) -> str:
    return f"""\
品目名  : {item_name}（品目コード: {item_code}）
現在在庫: {current_qty} {unit}
発注点  : {order_point} {unit}

確認URL : {settings.APP_URL}/stocks?alert=true

※このメールはTBN-IMSより自動送信されています。
"""
