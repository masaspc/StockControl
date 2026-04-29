from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SerialItem(Base):
    __tablename__ = "serial_items"
    __table_args__ = (
        CheckConstraint(
            "status IN ('in_stock','checked_out','disposed','lost')",
            name="serial_items_status_check",
        ),
        CheckConstraint(
            "condition IN ('normal','damaged','repair_needed')",
            name="serial_items_condition_check",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False
    )
    serial_no: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    mac_address: Mapped[str | None] = mapped_column(String(17))
    location_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("locations.id", ondelete="SET NULL"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="in_stock", nullable=False, index=True)
    condition: Mapped[str] = mapped_column(String(20), default="normal")
    received_at: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
