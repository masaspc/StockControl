from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class StockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    location_id: int
    quantity: int
    updated_at: datetime


class StockDetailResponse(StockResponse):
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    location_code: Optional[str] = None
    location_name: Optional[str] = None
    order_point: Optional[int] = None
    is_alert: bool = False


class StockSummary(BaseModel):
    total_items: int
    total_locations: int
    alert_items: int
    serial_items_total: int
    serial_items_in_stock: int
    serial_items_checked_out: int
