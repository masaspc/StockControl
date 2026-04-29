from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class SerialItemBase(BaseModel):
    item_id: int
    serial_no: str = Field(..., max_length=100)
    mac_address: Optional[str] = None
    location_id: Optional[int] = None
    received_at: Optional[date] = None


class SerialItemCreate(SerialItemBase):
    pass


class SerialItemUpdate(BaseModel):
    location_id: Optional[int] = None
    status: Optional[Literal["in_stock", "checked_out", "disposed", "lost"]] = None
    condition: Optional[Literal["normal", "damaged", "repair_needed"]] = None
    mac_address: Optional[str] = None


class SerialItemResponse(SerialItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    condition: str
    created_at: datetime
    updated_at: datetime
