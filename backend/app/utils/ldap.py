from __future__ import annotations

import logging

from ldap3 import ALL, Connection, Server

from app.core.config import settings

logger = logging.getLogger(__name__)


def ldap_authenticate(username: str, password: str) -> dict | None:
    """ADへバインド認証。成功時はユーザー属性dictを返す。"""
    if not settings.LDAP_ENABLED:
        return None
    try:
        server = Server(settings.LDAP_SERVER, get_info=ALL)
        # サービスアカウントで検索バインド
        conn = Connection(
            server,
            user=settings.LDAP_BIND_DN,
            password=settings.LDAP_BIND_PASSWORD,
            auto_bind=True,
        )
        search_filter = settings.LDAP_USER_SEARCH_FILTER.format(username=username)
        conn.search(
            settings.LDAP_BASE_DN,
            search_filter,
            attributes=["cn", "displayName", "mail", "sAMAccountName"],
        )
        if not conn.entries:
            logger.info("LDAP user not found: %s", username)
            return None
        user_dn = conn.entries[0].entry_dn
        user_attrs = conn.entries[0].entry_attributes_as_dict
        conn.unbind()

        # ユーザー本人のDN+パスワードでバインド試行
        user_conn = Connection(server, user=user_dn, password=password)
        if not user_conn.bind():
            logger.info("LDAP bind failed for user: %s", username)
            return None
        user_conn.unbind()
        return {
            "ad_account": username,
            "display_name": (user_attrs.get("displayName") or [username])[0],
            "email": (user_attrs.get("mail") or [None])[0],
        }
    except Exception:
        logger.exception("LDAP authentication error")
        return None
