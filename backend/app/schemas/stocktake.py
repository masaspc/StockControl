from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class StocktakeCreate(BaseModel):
    name: str
    location_id: Optional[int] = None
    note: Optional[str] = None


class StocktakeScan(BaseModel):
    item_id: int
    location_id: int
    counted_qty: int
    note: Optional[str] = None


class StocktakeSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location_id: Optional[int] = None
    status: str
    started_by: int
    note: Optional[str] = None
    started_at: datetime
    closed_at: Optional[datetime] = None


class StocktakeDiff(BaseModel):
    item_id: int
    item_code: str
    item_name: str
    location_id: int
    location_name: str
    expected_qty: int
    counted_qty: int
    diff: int
