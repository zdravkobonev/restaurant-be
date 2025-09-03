from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- твои текущи настройки ---
    DATABASE_URL: str

    # JWT / Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Lockout policy
    MAX_LOGIN_ATTEMPTS: int = 3
    LOCKOUT_MINUTES: int = 1

    # --- CORS (важно: държим ги като низове, НЕ като списъци) ---
    # Пристигат от Helm като CSV (напр. "http://ns-fe..."), или могат да са празни.
    CORS_ALLOW_ORIGINS: str = ""
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = ""
    CORS_ALLOW_HEADERS: str = ""
    CORS_EXPOSE_HEADERS: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
