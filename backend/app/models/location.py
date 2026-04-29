from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Location(Base):
    __tablename__ = "locations"
    __table_args__ = (
        CheckConstraint(
            "loc_type IN ('site','area','shelf','vehicle','person','customer')",
            name="locations_loc_type_check",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    loc_type: Mapped[str] = mapped_column(String(20), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("locations.id", ondelete="SET NULL")
    )
    site_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("locations.id", ondelete="SET NULL")
    )
    manager_id: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
