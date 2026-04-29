from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # アプリ
    APP_ENV: str = "development"
    APP_URL: str = "http://localhost"

    # JWT
    SECRET_KEY: str = "change-me-in-production-please-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # PostgreSQL
    POSTGRES_HOST: str = "tbn-ims-db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "tbn_ims"
    POSTGRES_USER: str = "tbn_ims_user"
    POSTGRES_PASSWORD: str = "password"

    # LDAP
    LDAP_ENABLED: bool = False
    LDAP_SERVER: str = ""
    LDAP_BASE_DN: str = ""
    LDAP_BIND_DN: str = ""
    LDAP_BIND_PASSWORD: str = ""
    LDAP_USER_SEARCH_FILTER: str = "(sAMAccountName={username})"

    # SMTP
    SMTP_ENABLED: bool = False
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "ims-noreply@tbn.local"
    SMTP_USE_TLS: bool = True

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
