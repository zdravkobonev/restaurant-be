from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from .routers import auth

def create_app() -> FastAPI:
    app = FastAPI(title="Admin Login API", version="1.0.0")

    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,              # ако някой ден пращаш cookies
        allow_methods=["*"],                 # GET, POST, PATCH, DELETE, OPTIONS...
        allow_headers=["*"],                 # Authorization, Content-Type, и т.н.
        expose_headers=["*"],                # по избор
    )

    app.include_router(auth.router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app

app = create_app()
