from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserMe
from app.schemas.common import Message
from app.utils.ldap import ldap_authenticate

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    # 1. ユーザー検索
    result = await db.execute(select(User).where(User.ad_account == payload.ad_account))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="認証に失敗しました")

    # 2. 認証: LDAP有効ならAD、無効ならローカルパスワード
    authenticated = False
    if settings.LDAP_ENABLED:
        ldap_user = ldap_authenticate(payload.ad_account, payload.password)
        authenticated = ldap_user is not None
    else:
        if user.password_hash and verify_password(payload.password, user.password_hash):
            authenticated = True

    if not authenticated:
        raise HTTPException(status_code=401, detail="認証に失敗しました")

    # 3. JWT発行
    access = create_access_token(subject=user.ad_account, role=user.role)
    refresh = create_refresh_token(subject=user.ad_account)

    user.last_login = datetime.now(timezone.utc)
    await db.flush()

    secure = settings.is_production
    response.set_cookie(
        "access_token",
        access,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        "refresh_token",
        refresh,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/v1/auth",
    )

    return TokenResponse(
        access_token=access,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    db: AsyncSession = Depends(get_db),
    refresh_token: str | None = None,
) -> TokenResponse:
    from fastapi import Cookie

    # 簡略実装: cookieから取得（本来はDependsで）
    raise HTTPException(status_code=501, detail="未実装: 直接 /login を使用してください")


@router.post("/logout", response_model=Message)
async def logout(response: Response) -> Message:
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/v1/auth")
    return Message(message="ログアウトしました")


@router.get("/me", response_model=UserMe)
async def me(current_user: User = Depends(get_current_user)) -> UserMe:
    return UserMe.model_validate(current_user)
