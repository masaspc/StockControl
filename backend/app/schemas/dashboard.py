from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AlertItem(BaseModel):
    item_id: int
    item_code: str
    item_name: str
    current_qty: int
    order_point: int
    unit: str


class RecentTransaction(BaseModel):
    id: int
    tx_type: str
    item_name: str
    quantity: int
    operator_name: Optional[str] = None
    created_at: datetime


class DashboardResponse(BaseModel):
    total_items: int
    total_locations: int
    total_serials: int
    alert_count: int
    pending_orders: int
    today_in: int
    today_out: int
    alerts: List[AlertItem] = []
    recent_transactions: List[RecentTransaction] = []
