from __future__ import annotations

import io
import os
from datetime import date
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

_FONT_REGISTERED = False
_FONT_NAME = "IPAexGothic"
_FONT_PATHS = [
    "/fonts/ipaexg.ttf",
    "/usr/share/fonts/opentype/ipaexfont-gothic/ipaexg.ttf",
]


def _ensure_font() -> str:
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return _FONT_NAME
    for path in _FONT_PATHS:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(_FONT_NAME, path))
            _FONT_REGISTERED = True
            return _FONT_NAME
    return "Helvetica"


def render_purchase_order_pdf(
    order_no: str,
    supplier_name: Optional[str],
    item_code: str,
    item_name: str,
    quantity: int,
    unit: str,
    expected_at: Optional[date],
    note: Optional[str],
    company_name: str = "東京ベイネットワーク株式会社",
) -> bytes:
    font_name = _ensure_font()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=40,
    )

    base_styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title",
        parent=base_styles["Title"],
        fontName=font_name,
        fontSize=20,
        alignment=1,
    )
    normal = ParagraphStyle("normal", parent=base_styles["Normal"], fontName=font_name, fontSize=11)
    small = ParagraphStyle("small", parent=base_styles["Normal"], fontName=font_name, fontSize=9)

    story = []
    story.append(Paragraph("発 注 書", title_style))
    story.append(Spacer(1, 16))
    story.append(Paragraph(f"発注番号: {order_no}", normal))
    story.append(Paragraph(f"発行日: {date.today().isoformat()}", normal))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"発注先: {supplier_name or '（未指定）'}", normal))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"発注元: {company_name}", normal))
    story.append(Spacer(1, 24))

    data = [
        ["品目コード", "品目名", "数量", "単位", "希望納期"],
        [
            item_code,
            item_name,
            str(quantity),
            unit,
            expected_at.isoformat() if expected_at else "-",
        ],
    ]
    table = Table(data, colWidths=[80, 220, 50, 50, 80])
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), font_name, 10),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (2, 1), (3, 1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 24))

    if note:
        story.append(Paragraph("備考:", normal))
        story.append(Paragraph(note.replace("\n", "<br/>"), small))

    doc.build(story)
    return buffer.getvalue()
