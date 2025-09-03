from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import auth


def _split_csv_or_jsonish(s: str) -> List[str]:
    """
    Приемаме CSV низ (напр. "GET,POST") или празно; връщаме списък.
    (Не разчитаме на JSON; достатъчно ни е CSV.)
    """
    if not s:
        return []
    return [p.strip() for p in s.split(",") if p.strip()]


def create_app() -> FastAPI:
    app = FastAPI(title="Admin Login API", version="1.0.0")

    # Origins: ако няма подадени от Helm/env → fall back към dev
    origins = _split_csv_or_jsonish(settings.CORS_ALLOW_ORIGINS)
    if not origins:
        origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]

    allow_methods = _split_csv_or_jsonish(settings.CORS_ALLOW_METHODS) or ["*"]
    allow_headers = _split_csv_or_jsonish(settings.CORS_ALLOW_HEADERS) or ["*"]
    expose_headers = _split_csv_or_jsonish(settings.CORS_EXPOSE_HEADERS) or None

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        expose_headers=expose_headers,
    )

    app.include_router(auth.router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
