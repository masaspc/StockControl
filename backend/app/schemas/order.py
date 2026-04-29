from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class OrderBase(BaseModel):
    item_id: int
    supplier_id: Optional[int] = None
    quantity: int
    expected_at: Optional[date] = None
    note: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    supplier_id: Optional[int] = None
    quantity: Optional[int] = None
    expected_at: Optional[date] = None
    note: Optional[str] = None
    status: Optional[
        Literal["draft", "pending", "approved", "ordered", "partial", "completed", "cancelled"]
    ] = None


class OrderResponse(OrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_no: str
    status: str
    requested_by: Optional[int] = None
    approved_by: Optional[int] = None
    ordered_at: Optional[date] = None
    created_at: datetime
    updated_at: datetime
