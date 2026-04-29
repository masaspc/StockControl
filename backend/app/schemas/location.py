from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class LocationBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    loc_type: Literal["site", "area", "shelf", "vehicle", "person", "customer"]
    parent_id: Optional[int] = None
    site_id: Optional[int] = None
    manager_id: Optional[int] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    site_id: Optional[int] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None


class LocationResponse(LocationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime


class LocationTreeNode(LocationResponse):
    children: List["LocationTreeNode"] = []


LocationTreeNode.model_rebuild()
