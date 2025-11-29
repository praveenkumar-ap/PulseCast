import logging
from fastapi import FastAPI

from routes import router
from routes_auth import router as auth_router
from fastapi import APIRouter


def configure_logging() -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def create_app() -> FastAPI:
    """Create and configure the FastAPI app."""
    configure_logging()
    app = FastAPI(title="svc-forecast")
    app.include_router(router)
    app.include_router(auth_router)
    # Compatibility prefix for clients using /api/*
    api_router = APIRouter(prefix="/api")
    api_router.include_router(router)
    api_router.include_router(auth_router)
    app.include_router(api_router)
    return app


app = create_app()
