from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import auth


def create_app() -> FastAPI:
    app = FastAPI(title="Admin Login API", version="1.0.0")

    # CORS от settings (подадени от Helm). Ако липсват → dev fallback.
    origins = settings.CORS_ALLOW_ORIGINS or [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    allow_methods = settings.CORS_ALLOW_METHODS or ["*"]
    allow_headers = settings.CORS_ALLOW_HEADERS or ["*"]
    expose_headers = settings.CORS_EXPOSE_HEADERS or None

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
