from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','pending','approved','ordered','partial','completed','cancelled')",
            name="orders_status_check",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("items.id"), nullable=False
    )
    supplier_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("suppliers.id")
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    requested_by: Mapped[int | None] = mapped_column(Integer)
    approved_by: Mapped[int | None] = mapped_column(Integer)
    ordered_at: Mapped[date | None] = mapped_column(Date)
    expected_at: Mapped[date | None] = mapped_column(Date)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
