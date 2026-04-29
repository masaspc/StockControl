from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Stock(Base):
    __tablename__ = "stocks"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="stocks_quantity_nonneg"),
        UniqueConstraint("item_id", "location_id", name="uq_stocks_item_location"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    location_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
