from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (
        CheckConstraint(
            "manage_type IN ('serial', 'quantity')", name="items_manage_type_check"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))
    maker: Mapped[str | None] = mapped_column(String(100))
    model_no: Mapped[str | None] = mapped_column(String(100))
    manage_type: Mapped[str] = mapped_column(String(20), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="個")
    order_point: Mapped[int] = mapped_column(Integer, default=0)
    order_unit: Mapped[int] = mapped_column(Integer, default=1)
    barcode: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
