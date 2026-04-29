from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    maker: Optional[str] = Field(None, max_length=100)
    model_no: Optional[str] = Field(None, max_length=100)
    manage_type: Literal["serial", "quantity"]
    unit: str = "個"
    order_point: int = 0
    order_unit: int = 1
    barcode: Optional[str] = Field(None, max_length=100)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = None
    maker: Optional[str] = None
    model_no: Optional[str] = None
    unit: Optional[str] = None
    order_point: Optional[int] = None
    order_unit: Optional[int] = None
    barcode: Optional[str] = None
    is_active: Optional[bool] = None


class ItemResponse(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
