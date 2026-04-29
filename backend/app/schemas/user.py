from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    ad_account: str = Field(..., max_length=100)
    display_name: str = Field(..., max_length=100)
    email: Optional[EmailStr] = None
    role: Literal["admin", "manager", "operator", "viewer"] = "viewer"
    site_id: Optional[int] = None


class UserCreate(UserBase):
    password: Optional[str] = None  # LDAP無効時のローカル認証用


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Literal["admin", "manager", "operator", "viewer"]] = None
    site_id: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
