from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint(
            "tx_type IN ('in','out','return','transfer','adjust')",
            name="transactions_tx_type_check",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tx_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("items.id"), nullable=False, index=True
    )
    serial_item_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("serial_items.id")
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    from_location_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("locations.id")
    )
    to_location_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("locations.id")
    )
    operator_id: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    work_order_no: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
