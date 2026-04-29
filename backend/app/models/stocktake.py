from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StocktakeSession(Base):
    __tablename__ = "stocktake_sessions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('open','closed','cancelled')",
            name="stocktake_sessions_status_check",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("locations.id"))
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)
    started_by: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class StocktakeRecord(Base):
    __tablename__ = "stocktake_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stocktake_sessions.id", ondelete="CASCADE"), nullable=False
    )
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("locations.id"), nullable=False
    )
    expected_qty: Mapped[int] = mapped_column(Integer, default=0)
    counted_qty: Mapped[int] = mapped_column(Integer, default=0)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
