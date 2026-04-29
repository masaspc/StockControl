from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    ad_account: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserMe(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ad_account: str
    display_name: str
    email: Optional[str] = None
    role: str
    site_id: Optional[int] = None
    last_login: Optional[datetime] = None
