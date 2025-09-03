from __future__ import annotations

import json
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    # JWT / Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Lockout policy
    MAX_LOGIN_ATTEMPTS: int = 3
    LOCKOUT_MINUTES: int = 1

    # --- CORS (идват от Helm като env; CSV или JSON списък) ---
    CORS_ALLOW_ORIGINS: List[str] = Field(default_factory=list)
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = Field(default_factory=list)
    CORS_ALLOW_HEADERS: List[str] = Field(default_factory=list)
    CORS_EXPOSE_HEADERS: List[str] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @field_validator(
        "CORS_ALLOW_ORIGINS",
        "CORS_ALLOW_METHODS",
        "CORS_ALLOW_HEADERS",
        "CORS_EXPOSE_HEADERS",
        mode="before",
    )
    @classmethod
    def _split_csv_or_json(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, (list, tuple)):
            return list(v)
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                try:
                    parsed = json.loads(s)
                    if isinstance(parsed, list):
                        return [str(x).strip() for x in parsed if str(x).strip()]
                except Exception:
                    pass
            return [p.strip() for p in s.split(",") if p.strip()]
        return [str(v)]

settings = Settings()
