"""初期管理者ユーザーを作成するスクリプト

使用例:
    docker exec -it tbn-ims-api python scripts/create_admin.py
"""
from __future__ import annotations

import asyncio
import getpass
import sys

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User


async def main() -> int:
    print("=== TBN-IMS 初期管理者作成 ===")
    ad_account = input("ADアカウント名 (例: admin): ").strip() or "admin"
    display_name = input("表示名 [管理者]: ").strip() or "管理者"
    email = input("メール (任意): ").strip() or None
    password = getpass.getpass("パスワード: ")
    if len(password) < 8:
        print("パスワードは8文字以上にしてください。", file=sys.stderr)
        return 1

    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(User).where(User.ad_account == ad_account))
        if existing.scalar_one_or_none():
            print(f"ユーザー '{ad_account}' は既に存在します。", file=sys.stderr)
            return 1
        user = User(
            ad_account=ad_account,
            display_name=display_name,
            email=email,
            role="admin",
            password_hash=hash_password(password),
            is_active=True,
        )
        db.add(user)
        await db.commit()
    print(f"作成しました: {ad_account} (admin)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
